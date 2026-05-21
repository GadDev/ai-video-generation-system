FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV UPLOAD_DIR=/tmp/uploads
ENV OUTPUT_DIR=/outputs
ENV MODEL_CHECKPOINT=stabilityai/stable-diffusion-xl-base-1.0
ENV HF_HOME=/root/.cache/huggingface
# Suppress OpenBLAS warnings
ENV OPENBLAS_NUM_THREADS=1

RUN mkdir -p /outputs /tmp/uploads $HF_HOME

EXPOSE 8000

# Run with 2 workers so status requests don't block during long generations
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
