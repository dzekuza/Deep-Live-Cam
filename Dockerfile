# Use official Python runtime  
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglu1-mesa \
    libglu1-mesa-dev \
    curl \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Docker-specific requirements and install Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY . .

# Download AI models
RUN mkdir -p models && \
    curl -L -o models/inswapper_128_fp16.onnx \
    "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx" && \
    curl -L -o models/GFPGANv1.4.pth \
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"

# Expose port for web interface
EXPOSE 8000

# Create entrypoint script for headless operation
RUN echo '#!/bin/bash\n\
if [ "$1" = "web" ]; then\n\
    python web_api.py\n\
else\n\
    python run.py "$@"\n\
fi' > entrypoint.sh && chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["web"] 