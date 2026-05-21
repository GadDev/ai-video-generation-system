FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV UPLOAD_DIR=/tmp/uploads
ENV OUTPUT_DIR=/outputs
ENV MODEL_CHECKPOINT=Animagine/Animagine-XL-3.0
ENV HF_HOME=/root/.cache/huggingface

RUN mkdir -p /outputs /tmp/uploads $HF_HOME

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
