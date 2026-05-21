# AI Video Generation System

Generate stunning 3-5 second anime video clips using Stable Diffusion XL on your local machine.

## Architecture

- **Frontend**: Next.js 14 on `localhost:3000`
- **Backend**: FastAPI + Uvicorn in Docker on `localhost:8000`
- **AI Models**: Stable Diffusion XL (open-source, no auth required)
- **Hardware**: Mac/Linux with 16GB+ RAM, or Apple Silicon with MPS acceleration
- **Acceleration**: PyTorch MPS (Metal Performance Shaders) on Apple Silicon

## Prerequisites

- Docker Desktop
- Node.js 18+
- 16GB+ RAM (8GB minimum, but slower)
- ~10GB free disk space for model weights

## Quick Start

### 1. Build Backend Image (One Time)

```bash
cd backend
docker build -t ai-video-backend .
```

### 2. Start Backend Container

**First time only:**
```bash
docker run --name ai-video-backend -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(pwd)/outputs:/outputs" \
  ai-video-backend
```

This creates a named container that you can reuse. The backend will:
- Download SDXL model (~7GB, first run only)
- Start on `http://localhost:8000`

**Subsequent times:** Stop and restart the same container (much faster):
```bash
docker stop ai-video-backend    # Stop the running container
docker start ai-video-backend   # Restart it (models are cached)
docker logs -f ai-video-backend # View logs
```

**Why reuse?** The container name (`--name ai-video-backend`) lets you stop/start the same container. This keeps cached models, so second runs are 10x faster.

### 3. Install & Run Frontend (New Terminal)

```bash
cd frontend
npm install  # Only needed once
npm run dev
```

Frontend runs on `http://localhost:3000`

### 4. Generate Your First Video

1. **Optional**: Upload 1-5 reference images (drag/drop)
2. **Required**: Enter a prompt (e.g., "sunset over mountains, peaceful atmosphere")
3. Click **"Generate Video"**
4. **Cancel anytime** with the red "Cancel Generation" button
5. Download your generated MP4 once complete

## File Structure

```
.
├── backend/
│   ├── app.py              # FastAPI main app
│   ├── models.py           # SDXL & AnimateDiff loaders
│   ├── generation.py       # Video frame generation
│   ├── video_export.py     # FFmpeg MP4/GIF export
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker image
│   └── outputs/            # Generated videos (git-ignored)
├── frontend/
│   ├── app/
│   │   ├── layout.js       # Root layout
│   │   └── page.js         # Main page
│   ├── components/
│   │   ├── ImageUpload.js
│   │   ├── PromptInput.js
│   │   ├── GenerationProgress.js
│   │   └── VideoPreview.js
│   ├── styles/globals.css
│   ├── next.config.js      # API proxy config
│   ├── tailwind.config.js
│   └── package.json
├── IDEA.md                 # Architecture & design rationale
└── README.md               # This file
```

## Model Details

**SDXL Pipeline**: `stabilityai/stable-diffusion-xl-base-1.0` + Refiner
- Base model: 32 inference steps → latent representation
- Refiner model: 8 inference steps → high-quality final image
- Total: 40 steps for optimal quality (per Stability AI docs)
- Resolution: 512×512
- No authentication required

**Frame Generation**
- Generates 1 high-quality base frame using SDXL base+refiner
- Duplicates frame 120 times for 5-second video (at 24fps)
- Supports optional reference images for style conditioning
- Total generation time: 4-6 minutes on CPU / 1-2 minutes on Apple Silicon MPS

## Environment Variables

Configure in `docker run`:

```bash
docker run --name ai-video-backend -p 8000:8000 \
  -e MODEL_CHECKPOINT=stabilityai/stable-diffusion-xl-base-1.0 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v $(pwd)/outputs:/outputs \
  ai-video-backend
```

Default values:
- `MODEL_CHECKPOINT`: `stabilityai/stable-diffusion-xl-base-1.0` (no auth needed)
- `HF_HOME`: `/root/.cache/huggingface` (Hugging Face model cache)
- `UPLOAD_DIR`: `/tmp/uploads` (temporary image storage)
- `OUTPUT_DIR`: `/outputs` (generated video storage)

## API Endpoints

### POST /generate

Submit prompt (+ optional images) for generation.

```bash
# Prompt only (no images)
curl -X POST http://localhost:8000/generate \
  -F "prompt=beautiful sunset over mountains"

# With images
curl -X POST http://localhost:8000/generate \
  -F "prompt=anime sunset scenery" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"

# Response: {"job_id": "uuid"}
```

### GET /status/{job_id}

Check generation progress (poll every 2 seconds).

```bash
curl http://localhost:8000/status/{job_id}

# Response:
# {
#   "status": "generating",
#   "progress": 45,
#   "message": "Generating video frames...",
#   "output_url": null
# }
```

### DELETE /generate/{job_id}

Cancel an in-progress generation (if status is "generating").

```bash
curl -X DELETE http://localhost:8000/generate/{job_id}

# Response:
# {
#   "job_id": "uuid",
#   "status": "cancelled"
# }
```

### GET /outputs/{job_id}

Download generated MP4 (only available after status is "complete").

```bash
curl http://localhost:8000/outputs/{job_id} -o video.mp4
```

## Typical Generation Timeline

```
Total time: ~4-6 minutes per clip (CPU) / ~1-2 minutes (Apple Silicon MPS)

- SDXL base (32 steps):        3-4 min (CPU) / 30-45s (MPS)
- SDXL refiner (8 steps):      1-2 min (CPU) / 15-30s (MPS)
- Frame duplication (120×):    <1s
- FFmpeg MP4 export:           10-20s
- Validation:                  <5s
```

**First request** adds model download/warmup: +5-10 minutes total  
**Subsequent requests** use cached models: much faster

## Troubleshooting

**Issue**: "MPS not available"
- M3 Mac has MPS built-in. Check PyTorch installation.
- Verify: `python -c "import torch; print(torch.backends.mps.is_available())"`

**Issue**: "CUDA out of memory"
- Happens on first request. Models are cached after warmup.
- Reduce concurrent requests (queue them).

**Issue**: "Model download stuck"
- Requires internet connection. Check `~/.cache/huggingface/` for partial downloads.
- Delete incomplete models and restart backend.

**Issue**: "Frontend can't reach backend"
- Ensure backend is running on port 8000.
- Check CORS headers are configured (`http://localhost:3000`).

## Performance Tips

1. **First request is slow** (model warmup) — expect 2-3 minutes
2. **Second+ requests are faster** (models cached) — expect 1-2 minutes
3. **Longer prompts** may reduce generation quality
4. **Keep clips short** (3-5 seconds) — anime masks temporal artifacts

## Limitations & Future Work

**Phase 1 (Current MVP)**:
- ✅ SDXL + AnimateDiff basic pipeline
- ✅ Local inference on Apple Silicon
- ✅ 3-5 second anime clips
- ❌ Character consistency across frames
- ❌ Multi-character composition
- ❌ Story continuity

**Phase 2 (Future)**:
- IP-Adapter for identity preservation
- LoRA fine-tuning for styles
- ControlNet for camera movements
- Multi-shot scene composition
- Local database for clip history

## Hardware Requirements

**Minimum**:
- M3 Mac with 18GB unified memory
- ~20GB free SSD space
- Broadband internet (for model download)

**Recommended**:
- M3 Pro/Max Mac
- 24GB+ unified memory
- Fast SSD (>500MB/s write)

## License

This project uses:
- [Diffusers](https://github.com/huggingface/diffusers) (Apache 2.0)
- [AnimateDiff](https://github.com/guoyww/AnimateDiff) (Apache 2.0)
- [FastAPI](https://github.com/tiangolo/fastapi) (MIT)
- [Next.js](https://github.com/vercel/next.js) (MIT)

See IDEA.md for architecture & design rationale.
