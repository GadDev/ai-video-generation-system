# AI Video Generation System

Generate stunning 3-5 second anime video clips using Stable Diffusion XL + AnimateDiff on your M3 Mac.

## Architecture

- **Frontend**: Next.js 14 on `localhost:3000`
- **Backend**: FastAPI + Uvicorn in Docker on `localhost:8000`
- **AI Models**: Stable Diffusion XL (Animagine) + AnimateDiff
- **Hardware**: Apple Silicon M3 Mac with 18GB+ unified memory
- **Acceleration**: PyTorch MPS (Metal Performance Shaders)

## Prerequisites

- Docker Desktop for Mac
- Node.js 18+
- M3 Mac with 18GB unified memory (recommended)
- ~20GB free disk space for model weights

## Quick Start

### 1. Build & Run Backend

```bash
cd backend
docker build -t ai-video-backend .
docker run -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v $(pwd)/outputs:/outputs \
  ai-video-backend
```

The backend will:
- Download SDXL and AnimateDiff models (first run only, ~10GB)
- Verify MPS acceleration
- Start on `http://localhost:8000`

First request takes 2-3 minutes (model warmup). Subsequent requests: 1-2 minutes.

### 2. Install & Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Generate Your First Video

1. Upload 2-5 anime reference images
2. Enter a prompt (e.g., "anime cyberpunk rooftop at sunset, cinematic camera movement")
3. Click "Generate Video"
4. Wait for generation (watch progress bar)
5. Download your generated MP4

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

**SDXL Checkpoint**: Animagine XL 3.0 (anime-tuned Stable Diffusion XL)
- Size: ~7GB
- Generates 1024×1024 images in 30-60 seconds
- Best with anime/illustration-style prompts

**AnimateDiff Motion Module**
- Generates 16-32 temporally coherent frames from static image
- Creates 0.67-1.33 second video clips (at 24fps)
- Offloads to MPS for Apple Silicon acceleration

## Environment Variables

Configure in `docker run` or modify `backend/app.py`:

```bash
MODEL_CHECKPOINT=Animagine/Animagine-XL-3.0  # Anime SDXL model
HF_HOME=/root/.cache/huggingface              # Hugging Face cache
UPLOAD_DIR=/tmp/uploads                       # Temp image storage
OUTPUT_DIR=/outputs                           # Generated video storage
```

## API Endpoints

### POST /generate

Submit images + prompt for generation.

```bash
curl -X POST http://localhost:8000/generate \
  -F "prompt=anime sunset scenery" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"

# Response: {"job_id": "uuid"}
```

### GET /status/{job_id}

Check generation progress.

```bash
curl http://localhost:8000/status/{job_id}

# Response:
# {
#   "status": "generating",
#   "progress": 45,
#   "message": "Exporting to MP4...",
#   "output_url": "/outputs/{job_id}"
# }
```

### GET /outputs/{job_id}

Download generated MP4.

```bash
curl http://localhost:8000/outputs/{job_id} -o video.mp4
```

## Typical Generation Timeline

```
Total time: ~2-3 minutes per clip

- SDXL frame generation: 30-60s
- AnimateDiff (16 frames):  45-90s
- FFmpeg MP4 export:        10-30s
- Validation:               5-10s
```

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
