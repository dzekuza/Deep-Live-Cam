#!/usr/bin/env python3
"""
Simple test to verify Deep-Live-Cam dependencies are working
"""

print("🧪 Testing Deep-Live-Cam dependencies...")

try:
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy: {e}")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

try:
    import onnxruntime
    print(f"✅ ONNX Runtime: {onnxruntime.__version__}")
except ImportError as e:
    print(f"❌ ONNX Runtime: {e}")

try:
    import insightface
    print(f"✅ InsightFace: {insightface.__version__}")
except ImportError as e:
    print(f"❌ InsightFace: {e}")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch: {e}")

try:
    # Test if models exist
    import os
    models_path = "models"
    if os.path.exists(f"{models_path}/inswapper_128_fp16.onnx"):
        print("✅ Face swapping model found")
    else:
        print("❌ Face swapping model missing")
        
    if os.path.exists(f"{models_path}/GFPGANv1.4.pth"):
        print("✅ Face enhancement model found")
    else:
        print("❌ Face enhancement model missing")
except Exception as e:
    print(f"❌ Model check failed: {e}")

print("\n🎯 Testing face detection...")
try:
    # Test basic face detection
    import cv2
    from modules.face_analyser import get_one_face
    
    # Create a simple test image
    test_image = np.ones((300, 300, 3), dtype=np.uint8) * 128
    
    # This will fail gracefully if no face is found, which is expected
    face = get_one_face(test_image)
    if face is None:
        print("✅ Face detection module working (no face found in test image - this is expected)")
    else:
        print("✅ Face detection module working")
        
except Exception as e:
    print(f"❌ Face detection test failed: {e}")

print("\n🚀 Summary:")
print("If all core dependencies show ✅, the application should work!")
print("You can now try to run the web interface or use the command line version.")

print("\n💡 Quick start options:")
print("1. Command line: python run.py --source face1.jpg --target face2.jpg --output result.jpg")
print("2. GUI version: python run.py")
print("3. Web interface: python web_api.py (if all dependencies work)") 