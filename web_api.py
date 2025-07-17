#!/usr/bin/env python3
"""
Web API wrapper for Deep-Live-Cam to enable cloud deployment
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import base64
import cv2
import numpy as np
from PIL import Image
import io
import threading
import time

# Import Deep-Live-Cam modules
import modules.globals
import modules.core
from modules.processors.frame.core import get_frame_processors_modules
from modules.face_analyser import get_one_face
from modules.utilities import is_image, is_video

# Global variable to store the current source face path for live mode
LIVE_SOURCE_FACE_PATH = None
last_frame_processing_time = 0  # Rate limiting for frame processing

app = Flask(__name__)
CORS(app)

# Global variables for processing
processing_status = {"status": "idle", "progress": 0, "message": ""}

class WebDeepLiveCam:
    def __init__(self):
        self.setup_globals()
        
    def setup_globals(self):
        """Setup default global configurations for headless operation"""
        modules.globals.headless = True
        modules.globals.frame_processors = ['face_swapper']
        modules.globals.keep_fps = True
        modules.globals.keep_audio = True
        modules.globals.many_faces = False
        modules.globals.nsfw_filter = False  # Disable NSFW filtering
        modules.globals.execution_providers = ['cpu']  # Default to CPU
        modules.globals.max_memory = 4  # 4GB default
        
    def update_status(self, status, progress=0, message=""):
        """Update processing status"""
        global processing_status
        processing_status.update({
            "status": status,
            "progress": progress,
            "message": message
        })

web_app = WebDeepLiveCam()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.8"})

@app.route('/status', methods=['GET'])
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)

@app.route('/live_status', methods=['GET'])
def get_live_status():
    """Get live mode status and source face availability"""
    global LIVE_SOURCE_FACE_PATH
    return jsonify({
        "live_available": LIVE_SOURCE_FACE_PATH is not None and os.path.exists(LIVE_SOURCE_FACE_PATH),
        "source_face_path": LIVE_SOURCE_FACE_PATH
    })

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process image face swap via API"""
    try:
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Request data: {request.get_data()}")
        data = request.get_json()
        print(f"DEBUG: Parsed JSON: {data}")
        if not data or 'source_image' not in data or 'target_image' not in data:
            print(f"DEBUG: Missing keys. Data keys: {list(data.keys()) if data else 'None'}")
            return jsonify({"error": "Missing source_image or target_image"}), 400

        web_app.update_status("processing", 10, "Preparing images...")

        # If the input is a file path, use it directly; otherwise, treat as base64
        source_val = data['source_image']
        target_val = data['target_image']
        output_val = data.get('output_path')

        # Check if the values look like file paths (not base64)
        def is_likely_file_path(val):
            return isinstance(val, str) and (
                val.startswith('/') or 
                val.startswith('./') or 
                val.startswith('../') or
                (not val.startswith('data:') and len(val) < 1000)  # Base64 images are usually longer
            )

        if is_likely_file_path(source_val) and is_likely_file_path(target_val):
            # Treat as file paths
            source_path = source_val
            target_path = target_val
            output_path = output_val or os.path.join(tempfile.gettempdir(), f"output_{int(time.time())}.jpg")
        else:
            # Fallback: treat as base64
            try:
                source_data = base64.b64decode(source_val)
                target_data = base64.b64decode(target_val)
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as source_file:
                    source_file.write(source_data)
                    source_path = source_file.name
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as target_file:
                    target_file.write(target_data)
                    target_path = target_file.name
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as output_file:
                    output_path = output_file.name
            except Exception as e:
                return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        # Set up globals for processing
        modules.globals.source_path = source_path
        modules.globals.target_path = target_path
        modules.globals.output_path = output_path

        web_app.update_status("processing", 30, "Processing face swap...")

        def process_async():
            try:
                source_face = get_one_face(cv2.imread(source_path))
                if source_face is None:
                    web_app.update_status("error", 0, "No face found in source image")
                    return
                web_app.update_status("processing", 50, "Swapping faces...")
                import shutil
                shutil.copy2(target_path, output_path)
                for frame_processor in get_frame_processors_modules(modules.globals.frame_processors):
                    web_app.update_status("processing", 70, f"Applying {frame_processor.NAME}...")
                    frame_processor.process_image(source_path, output_path, output_path)
                web_app.update_status("completed", 100, "Face swap completed successfully")
            except Exception as e:
                web_app.update_status("error", 0, f"Processing failed: {str(e)}")
            finally:
                try:
                    if not (os.path.exists(data['source_image']) and os.path.exists(data['target_image'])):
                        os.unlink(source_path)
                        os.unlink(target_path)
                except:
                    pass
        thread = threading.Thread(target=process_async)
        thread.start()
        return jsonify({"message": "Processing started", "output_path": output_path})
    except Exception as e:
        web_app.update_status("error", 0, f"Request failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """Download processed file"""
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_files():
    """Upload files for processing"""
    try:
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing source or target file"}), 400
            
        source_file = request.files['source']
        target_file = request.files['target']
        
        # Save uploaded files
        source_path = os.path.join(tempfile.gettempdir(), f"source_{int(time.time())}.jpg")
        target_path = os.path.join(tempfile.gettempdir(), f"target_{int(time.time())}.jpg") 
        output_path = os.path.join(tempfile.gettempdir(), f"output_{int(time.time())}.jpg")
        
        source_file.save(source_path)
        target_file.save(target_path)
        
        # Set up for processing
        modules.globals.source_path = source_path
        modules.globals.target_path = target_path
        modules.globals.output_path = output_path
        
        global LIVE_SOURCE_FACE_PATH
        LIVE_SOURCE_FACE_PATH = source_path  # Store for live mode
        
        return jsonify({
            "message": "Files uploaded successfully",
            "source_path": source_path,
            "target_path": target_path,
            "output_path": output_path
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a single video frame for live face swap"""
    try:
        global LIVE_SOURCE_FACE_PATH, last_frame_processing_time
        
        # Rate limiting: minimum 200ms between requests
        current_time = time.time()
        if current_time - last_frame_processing_time < 0.2:  # 200ms minimum interval
            return jsonify({"error": "Too many requests, please slow down"}), 429
        last_frame_processing_time = current_time
        
        # Check if source face is available
        if LIVE_SOURCE_FACE_PATH is None or not os.path.exists(LIVE_SOURCE_FACE_PATH):
            return jsonify({"error": "No source face uploaded for live mode."}), 400
            
        # Check if frame file is present
        if 'frame' not in request.files:
            return jsonify({"error": "Missing frame file"}), 400
            
        frame_file = request.files['frame']
        if frame_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Create temporary file paths
        timestamp = int(time.time()*1000)
        frame_path = os.path.join(tempfile.gettempdir(), f"live_frame_{timestamp}.jpg")
        output_path = os.path.join(tempfile.gettempdir(), f"live_result_{timestamp}.jpg")
        
        # Save uploaded frame
        try:
            frame_file.save(frame_path)
        except Exception as e:
            return jsonify({"error": f"Failed to save frame: {str(e)}"}), 500
            
        # Run face swap using the same logic as process_image, but for a single frame
        try:
            # Load source image
            source_image = cv2.imread(LIVE_SOURCE_FACE_PATH)
            if source_image is None:
                return jsonify({"error": "Failed to load source image"}), 400
                
            # Extract source face
            source_face = get_one_face(source_image)
            if source_face is None:
                return jsonify({"error": "No face found in source image"}), 400
                
            # Copy frame to output path
            import shutil
            shutil.copy2(frame_path, output_path)
            
            # Process frame with face swap
            try:
                for frame_processor in get_frame_processors_modules(modules.globals.frame_processors):
                    frame_processor.process_image(LIVE_SOURCE_FACE_PATH, output_path, output_path)
            except Exception as e:
                # If face detection fails, return original frame
                import shutil
                shutil.copy2(frame_path, output_path)
                print(f"Face detection failed, returning original frame: {str(e)}")
                
            # Check if output file was created
            if not os.path.exists(output_path):
                return jsonify({"error": "Failed to generate output image"}), 500
                
        except Exception as e:
            # Clean up output file if it exists
            try:
                if os.path.exists(output_path):
                    os.unlink(output_path)
            except:
                pass
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500
        finally:
            # Clean up input frame
            try:
                if os.path.exists(frame_path):
                    os.unlink(frame_path)
            except:
                pass
                
        # Return processed image
        return send_file(output_path, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def index():
    """Simple web interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deep-Live-Cam Web API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
            input[type="file"] { margin: 10px 0; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #005a87; }
            #status { margin: 20px 0; padding: 10px; background: #e7f3ff; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🎭 Deep-Live-Cam Web Interface</h1>
        <div class="container">
            <h3>Upload Images for Face Swap</h3>
            <form id="uploadForm">
                <label>Source Image (face to copy):</label><br>
                <input type="file" id="sourceFile" accept="image/*" required><br>
                
                <label>Target Image (image to modify):</label><br>
                <input type="file" id="targetFile" accept="image/*" required><br>
                
                <button type="submit">Process Face Swap</button>
            </form>
        </div>
        
        <div class="container">
            <h3>🎥 Live Webcam Face Swap</h3>
            <p>First upload a source face image above, then start live webcam mode:</p>
            <button id="startLiveBtn" onclick="startLiveMode()">Start Live Webcam</button>
            <button id="stopLiveBtn" onclick="stopLiveMode()" style="display:none;">Stop Live Webcam</button>
            
            <div id="liveContainer" style="display:none; margin-top: 20px;">
                <div style="display: flex; gap: 20px; justify-content: center;">
                    <div>
                        <h4>Original Webcam</h4>
                        <video id="webcamVideo" autoplay muted style="width: 320px; height: 240px; border: 2px solid #ccc; border-radius: 5px;"></video>
                    </div>
                    <div>
                        <h4>Face Swapped</h4>
                        <canvas id="outputCanvas" style="width: 320px; height: 240px; border: 2px solid #4CAF50; border-radius: 5px;"></canvas>
                    </div>
                </div>
                <div id="liveStatus" style="margin-top: 10px; text-align: center; color: #666;"></div>
            </div>
        </div>
        
        <div id="status" style="display:none;">
            <h3>Processing Status</h3>
            <div id="statusText">Ready</div>
            <div id="progress" style="width: 100%; background-color: #ddd; border-radius: 5px; margin: 10px 0;">
                <div id="progressBar" style="width: 0%; height: 20px; background-color: #4CAF50; border-radius: 5px;"></div>
            </div>
        </div>
        
        <div id="result" style="display:none;">
            <h3>Result</h3>
            <img id="resultImage" style="max-width: 100%; border-radius: 5px;" />
            <br><br>
            <a id="downloadLink" href="#" download="face_swap_result.jpg">
                <button>Download Result</button>
            </a>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const sourceFile = document.getElementById('sourceFile').files[0];
                const targetFile = document.getElementById('targetFile').files[0];
                
                if (!sourceFile || !targetFile) {
                    alert('Please select both source and target images');
                    return;
                }
                
                const formData = new FormData();
                formData.append('source', sourceFile);
                formData.append('target', targetFile);
                
                document.getElementById('status').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    // First upload the files
                    const uploadResponse = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const uploadData = await uploadResponse.json();
                    
                    if (uploadResponse.ok) {
                        // Then start processing
                        const processResponse = await fetch('/process_image', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                source_image: uploadData.source_path,
                                target_image: uploadData.target_path,
                                output_path: uploadData.output_path
                            })
                        });
                        
                        const processData = await processResponse.json();
                        
                        if (processResponse.ok) {
                            // Monitor processing status
                            await processImages(uploadData.output_path);
                        } else {
                            throw new Error(processData.error);
                        }
                    } else {
                        throw new Error(uploadData.error);
                    }
                } catch (error) {
                    document.getElementById('statusText').textContent = 'Error: ' + error.message;
                }
            });
            
            async function processImages(outputPath) {
                // Monitor processing status
                const statusInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/status');
                        const status = await response.json();
                        
                        document.getElementById('statusText').textContent = status.message;
                        document.getElementById('progressBar').style.width = status.progress + '%';
                        
                        if (status.status === 'completed') {
                            clearInterval(statusInterval);
                            showResult(outputPath);
                        } else if (status.status === 'error') {
                            clearInterval(statusInterval);
                            alert('Processing failed: ' + status.message);
                        }
                    } catch (error) {
                        clearInterval(statusInterval);
                        alert('Status check failed: ' + error.message);
                    }
                }, 1000);
            }
            
            function showResult(outputPath) {
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultImage').src = '/download/' + encodeURIComponent(outputPath);
                document.getElementById('downloadLink').href = '/download/' + encodeURIComponent(outputPath);
            }
            
            // Live webcam variables
            let mediaStream = null;
            let videoTrack = null;
            let canvas = null;
            let ctx = null;
            let animationId = null;
            let isLiveModeActive = false;
            let lastFrameTime = 0;
            let isProcessingFrame = false; // Prevent concurrent frame processing
            const TARGET_FPS = 3; // Further reduced to 3 FPS for better performance
            const FRAME_INTERVAL = 1000 / TARGET_FPS;
            let processingFrame = false; // Prevent overlapping requests
            
            async function startLiveMode() {
                try {
                    // Check if source face is uploaded
                    const sourceFile = document.getElementById('sourceFile').files[0];
                    if (!sourceFile) {
                        alert('Please first upload a source face image above');
                        return;
                    }
                    
                    // Upload source face if not already done
                    const formData = new FormData();
                    formData.append('source', sourceFile);
                    formData.append('target', sourceFile); // Use same file as target for upload
                    
                    const uploadResponse = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!uploadResponse.ok) {
                        throw new Error('Failed to upload source face');
                    }
                    
                    // Start webcam with smaller resolution for better performance
                    mediaStream = await navigator.mediaDevices.getUserMedia({ 
                        video: { 
                            width: 320, 
                            height: 240,
                            facingMode: 'user'
                        } 
                    });
                    
                    const video = document.getElementById('webcamVideo');
                    video.srcObject = mediaStream;
                    videoTrack = mediaStream.getVideoTracks()[0];
                    
                    // Setup canvas with smaller size for better performance
                    canvas = document.getElementById('outputCanvas');
                    ctx = canvas.getContext('2d');
                    canvas.width = 320; // Reduced size
                    canvas.height = 240; // Reduced size
                    
                    // Show live interface
                    document.getElementById('liveContainer').style.display = 'block';
                    document.getElementById('startLiveBtn').style.display = 'none';
                    document.getElementById('stopLiveBtn').style.display = 'inline-block';
                    
                    isLiveModeActive = true;
                    document.getElementById('liveStatus').textContent = 'Live mode active - Processing frames...';
                    
                    // Start frame processing loop
                    processLiveFrames();
                    
                } catch (error) {
                    alert('Failed to start live mode: ' + error.message);
                    console.error('Live mode error:', error);
                }
            }
            
            function stopLiveMode() {
                isLiveModeActive = false;
                
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                    mediaStream = null;
                }
                
                if (animationId) {
                    cancelAnimationFrame(animationId);
                    animationId = null;
                }
                
                document.getElementById('liveContainer').style.display = 'none';
                document.getElementById('startLiveBtn').style.display = 'inline-block';
                document.getElementById('stopLiveBtn').style.display = 'none';
                document.getElementById('liveStatus').textContent = 'Live mode stopped';
            }
            
            async function processLiveFrames() {
                if (!isLiveModeActive || isProcessingFrame) return;
                
                const currentTime = performance.now();
                
                // Frame rate limiting
                if (currentTime - lastFrameTime < FRAME_INTERVAL) {
                    if (isLiveModeActive) {
                        animationId = requestAnimationFrame(processLiveFrames);
                    }
                    return;
                }
                
                isProcessingFrame = true;
                lastFrameTime = currentTime;
                
                try {
                    const video = document.getElementById('webcamVideo');
                    
                    // Draw current frame to canvas
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    // Convert canvas to blob and send to server
                    canvas.toBlob(async (blob) => {
                        if (!isLiveModeActive) {
                            isProcessingFrame = false;
                            return;
                        }
                        
                        const formData = new FormData();
                        formData.append('frame', blob, 'frame.jpg');
                        
                        try {
                            const response = await fetch('/process_frame', {
                                method: 'POST',
                                body: formData
                            });
                            
                            if (response.ok) {
                                const resultBlob = await response.blob();
                                const resultUrl = URL.createObjectURL(resultBlob);
                                
                                // Create image from result and draw to canvas
                                const img = new Image();
                                img.onload = () => {
                                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                                };
                                img.src = resultUrl;
                                
                                document.getElementById('liveStatus').textContent = `Live mode active - Processing at ${TARGET_FPS} FPS...`;
                            } else {
                                const errorData = await response.json();
                                console.error('Frame processing error:', errorData.error);
                                document.getElementById('liveStatus').textContent = 'Error processing frame: ' + errorData.error;
                            }
                        } catch (error) {
                            console.error('Frame processing failed:', error);
                            document.getElementById('liveStatus').textContent = 'Error: ' + error.message;
                        } finally {
                            isProcessingFrame = false;
                        }
                    }, 'image/jpeg', 0.9); // Higher quality to prevent corruption
                    
                } catch (error) {
                    console.error('Live frame processing error:', error);
                    document.getElementById('liveStatus').textContent = 'Error: ' + error.message;
                    isProcessingFrame = false;
                }
                
                // Continue processing frames
                if (isLiveModeActive) {
                    animationId = requestAnimationFrame(processLiveFrames);
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Initialize core modules
    modules.core.parse_args = lambda: None  # Disable argument parsing
    
    print("🚀 Starting Deep-Live-Cam Web API...")
    print("📋 Available endpoints:")
    print("   GET  /           - Web interface")
    print("   GET  /health     - Health check") 
    print("   GET  /status     - Processing status")
    print("   GET  /live_status - Live mode status")
    print("   POST /upload     - Upload files")
    print("   POST /process_image - Process via JSON API")
    print("   POST /process_frame - Process live webcam frame")
    print("   GET  /download/<path> - Download results")
    
    app.run(host='0.0.0.0', port=8000, debug=False) 