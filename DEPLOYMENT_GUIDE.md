# 🚀 Cloud Deployment Guide for Deep-Live-Cam

This guide provides multiple solutions for deploying Deep-Live-Cam to cloud platforms to solve hardware compatibility issues like the **AVX instruction error** you're experiencing.

## 🔧 **Why Cloud Deployment?**

- ✅ **Solves AVX instruction issues** on older hardware
- ✅ **Access to modern CPUs/GPUs** with full instruction set support
- ✅ **Scalable processing power** 
- ✅ **No local installation hassles**
- ✅ **Cross-platform compatibility**

## 🎯 **Deployment Options**

### **Option 1: Docker + GPU Cloud (Recommended)**

Best for: Production use, better performance, scalability

**Supported Platforms:**
- **Google Cloud Platform** (Compute Engine with GPU)
- **AWS** (EC2 with GPU instances) 
- **Azure** (GPU-enabled VMs)
- **DigitalOcean** (GPU Droplets)
- **Vast.ai** (Cheap GPU rentals)

#### **Quick Deploy Steps:**

1. **Build Docker Image:**
```bash
# Clone the repository (if not done already)
git clone https://github.com/hacksider/Deep-Live-Cam.git
cd Deep-Live-Cam

# Build Docker image
docker build -t deep-live-cam .
```

2. **Run Locally (for testing):**
```bash
# CPU only
docker run -p 8000:8000 deep-live-cam web

# With GPU (if available)
docker run --gpus all -p 8000:8000 deep-live-cam web
```

3. **Deploy to Cloud:**
```bash
# Example for Google Cloud
gcloud run deploy deep-live-cam \
  --image gcr.io/YOUR_PROJECT/deep-live-cam \
  --platform managed \
  --memory 4Gi \
  --cpu 2 \
  --port 8000
```

### **Option 2: Web API (Flask) - Easy Setup**

Best for: Quick testing, simple deployments, Heroku/Vercel alternative

#### **Run Web API:**

```bash
# Install additional dependencies
pip install flask flask-cors

# Start web server
python web_api.py
```

**Access at:** `http://localhost:8000`

#### **Deploy to Cloud:**

**Heroku (CPU only):**
```bash
# Create Procfile
echo "web: python web_api.py" > Procfile

# Deploy
heroku create your-app-name
git add .
git commit -m "Deploy Deep-Live-Cam"
git push heroku main
```

**Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### **Option 3: Hugging Face Spaces**

Best for: Free hosting, community sharing

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Choose "Gradio" or "Streamlit"** 
3. **Upload your code** with a `app.py` file:

```python
import gradio as gr
import cv2
import numpy as np
from PIL import Image

# Import Deep-Live-Cam modules
import modules.globals
from modules.processors.frame.core import get_frame_processors_modules
from modules.face_analyser import get_one_face

def face_swap(source_image, target_image):
    """Process face swap for Gradio interface"""
    try:
        # Setup globals for headless operation
        modules.globals.headless = True
        modules.globals.frame_processors = ['face_swapper']
        
        # Convert PIL Images to cv2 format
        source_cv2 = cv2.cvtColor(np.array(source_image), cv2.COLOR_RGB2BGR)
        target_cv2 = cv2.cvtColor(np.array(target_image), cv2.COLOR_RGB2BGR)
        
        # Check for faces
        source_face = get_one_face(source_cv2)
        if source_face is None:
            return None, "❌ No face found in source image"
        
        # Process face swap
        # ... (implement face swapping logic)
        
        return target_image, "✅ Face swap completed"
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# Create Gradio interface
iface = gr.Interface(
    fn=face_swap,
    inputs=[
        gr.Image(type="pil", label="Source Image (Face to copy)"),
        gr.Image(type="pil", label="Target Image (Image to modify)")
    ],
    outputs=[
        gr.Image(type="pil", label="Result"),
        gr.Textbox(label="Status")
    ],
    title="🎭 Deep-Live-Cam Face Swap",
    description="Upload two images to perform AI face swapping"
)

iface.launch()
```

## 🔧 **Platform-Specific Instructions**

### **Google Cloud Platform**

```bash
# 1. Create project and enable APIs
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# 2. Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/deep-live-cam
gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/deep-live-cam --platform managed
```

### **AWS EC2 with Docker**

```bash
# 1. Launch EC2 instance (recommend g4dn.xlarge for GPU)
# 2. Install Docker
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Deploy
docker run -d -p 80:8000 --name deep-live-cam deep-live-cam web
```

### **DigitalOcean App Platform**

Create `app.yaml`:
```yaml
name: deep-live-cam
services:
- name: web
  source_dir: /
  github:
    repo: your-username/Deep-Live-Cam
    branch: main
  run_command: python web_api.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8000
```

## 📊 **Performance Comparison**

| Platform | Setup Time | Cost/Month | GPU Support | Performance |
|----------|------------|------------|-------------|-------------|
| **Google Cloud Run** | ⭐⭐⭐⭐⭐ | $20-50 | ❌ | ⭐⭐⭐ |
| **AWS EC2 (GPU)** | ⭐⭐⭐ | $100-300 | ✅ | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | ⭐⭐⭐⭐⭐ | Free | ❌ | ⭐⭐ |
| **Vast.ai** | ⭐⭐⭐⭐ | $10-30 | ✅ | ⭐⭐⭐⭐⭐ |
| **Railway/Heroku** | ⭐⭐⭐⭐⭐ | $5-25 | ❌ | ⭐⭐⭐ |

## ⚡ **Quick Start Commands**

### **For Testing (Local Docker):**
```bash
# 1. Build and test locally
docker build -t deep-live-cam .
docker run -p 8000:8000 deep-live-cam web

# 2. Open browser to http://localhost:8000
```

### **For Production (Cloud Deploy):**
```bash
# 1. Choose your platform
# 2. Push Docker image to registry
# 3. Deploy with platform-specific commands above
```

## 🚨 **Important Notes**

- **Live Camera Features**: Not available in cloud deployment (webcam access requires local hardware)
- **Video Processing**: Works but may be slower on CPU-only instances
- **Model Size**: Initial download is ~600MB (be aware of bandwidth costs)
- **Memory Requirements**: Minimum 4GB RAM recommended
- **Security**: Implement proper authentication for production use

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Out of Memory**: Increase instance memory or use smaller models
2. **Slow Processing**: Upgrade to GPU instance 
3. **TensorFlow AVX Errors**: Should be resolved with modern cloud instances
4. **Model Download Fails**: Check internet connectivity and disk space

### **Testing Your Deployment:**

```bash
# Health check
curl https://your-app.com/health

# Upload test
curl -X POST -F "source=@face1.jpg" -F "target=@face2.jpg" \
  https://your-app.com/upload
```

## 💡 **Cost Optimization Tips**

1. **Use CPU-only instances** for basic testing ($5-20/month)
2. **Spot instances** for batch processing (50-90% savings)
3. **Auto-scaling** to zero when not in use
4. **CDN** for static assets and models
5. **Compress models** if possible

---

**✅ Ready to deploy?** Choose the option that best fits your needs and follow the platform-specific instructions above! 