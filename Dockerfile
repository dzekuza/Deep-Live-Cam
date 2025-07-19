# Multi-stage build to reduce final image size
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Final stage - minimal runtime image
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglu1-mesa \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create model download script
RUN echo '#!/bin/bash\n\
echo "Downloading AI models..."\n\
mkdir -p models\n\
if [ ! -f "models/inswapper_128_fp16.onnx" ]; then\n\
    curl -L -o models/inswapper_128_fp16.onnx \\\n\
    "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx"\n\
fi\n\
if [ ! -f "models/GFPGANv1.4.pth" ]; then\n\
    curl -L -o models/GFPGANv1.4.pth \\\n\
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"\n\
fi\n\
echo "Models downloaded successfully!"\n\
exec "$@"' > download_models.sh && chmod +x download_models.sh

# Expose port for web interface
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Download models if they don'\''t exist\n\
./download_models.sh\n\
\n\
if [ "$1" = "web" ]; then\n\
    python web_api.py\n\
else\n\
    python run.py "$@"\n\
fi' > entrypoint.sh && chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["web"] 