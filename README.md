# AI Video Generation System

Generate animated video clips from text prompts using AnimateDiff + AnimateLCM on your local machine.

## Architecture

- **Frontend**: Next.js 14 on `localhost:3000`
- **Backend**: FastAPI + Uvicorn in Docker on `localhost:8000`
- **AI Models**: AnimateDiff + AnimateLCM on SD 1.5 (open-source, no auth required)
- **Hardware**: Mac/Linux with 16GB+ RAM

## Prerequisites

- Python 3.11+
- Node.js 18+
- 16GB+ RAM (8GB minimum)
- ~15GB free disk space (models + outputs)
- Apple Silicon Mac recommended (for MPS GPU acceleration)

## Quick Start

### 1. Start Backend

```bash
./backend/run.sh
```

First run installs dependencies and downloads models (~5 min). Subsequent runs start in seconds.

### 2. Start Frontend (New Terminal)

```bash
cd frontend
npm install  # Only needed once
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Generate Your First Video

1. **Optional**: Upload 1-5 reference images (drag/drop)
2. **Required**: Enter a prompt (e.g., `"cat dancing under the moon, anime style"`)
3. Click **"Generate Video"**
4. Watch the progress bar — **~30-60 seconds on Apple Silicon MPS**
5. **Cancel anytime** with the red "Cancel Generation" button
6. Download your generated MP4 once complete

## File Structure

```
.
├── backend/
│   ├── app.py              # FastAPI main app
│   ├── models.py           # SDXL model loader
│   ├── generation.py       # Frame generation pipeline
│   ├── video_export.py     # FFmpeg MP4 export
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker image
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
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── package.json
├── outputs/                # Generated videos
├── STARTUP.md              # Step-by-step startup guide
└── README.md               # This file
```

## How It Works

1. **AnimateDiff** generates 16 frames of real animated motion from the text prompt (6 LCM steps)
2. **FFmpeg** assembles the 16 frames into an MP4 at 8fps (~2 seconds of animation)

> The video has real frame-to-frame motion — not a looped static image.

## Model Details

**Pipeline**: `AnimateDiffPipeline` + `AnimateLCM`
- Base model: `emilianJR/epiCRealism` (SD 1.5-based, 512×512 native resolution)
- Motion adapter: `wangfuyun/AnimateLCM` (generates temporally consistent motion)
- Scheduler: `LCMScheduler` — only 6 inference steps (vs 50 for standard AnimateDiff)
- Output: 16 frames at 8fps ≈ 2 seconds
- No authentication required

## Environment Variables

```bash
docker run --name ai-video-backend -p 8000:8000 \
  -e BASE_MODEL=emilianJR/epiCRealism \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(pwd)/outputs:/outputs" \
  ai-video-backend
```

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_MODEL` | `emilianJR/epiCRealism` | SD 1.5-based HuggingFace model ID |
| `HF_HOME` | `/root/.cache/huggingface` | Model cache directory |
| `UPLOAD_DIR` | `/tmp/uploads` | Temporary image uploads |
| `OUTPUT_DIR` | `/outputs` | Generated video output |

## API Endpoints

### POST /generate

```bash
# Prompt only
curl -X POST http://localhost:8000/generate \
  -F "prompt=beautiful sunset over mountains"

# With reference images
curl -X POST http://localhost:8000/generate \
  -F "prompt=anime sunset scenery" \
  -F "images=@image1.jpg"

# Response: {"job_id": "uuid"}
```

### GET /status/{job_id}

```bash
curl http://localhost:8000/status/{job_id}

# Response:
# {
#   "status": "generating",   # generating | complete | failed | cancelled
#   "progress": 35,
#   "message": "🎬 Generating base frame... 35%",
#   "output_url": null        # set to "/outputs/{job_id}" when complete
# }
```

### DELETE /generate/{job_id}

```bash
curl -X DELETE http://localhost:8000/generate/{job_id}
# Response: {"job_id": "uuid", "status": "cancelled"}
```

### GET /outputs/{job_id}

```bash
curl http://localhost:8000/outputs/{job_id} -o video.mp4
```

## Generation Timeline

```
                        Apple Silicon MPS    CPU only
AnimateLCM (6 steps):  30-60s               3-5 min
FFmpeg export:         ~15s                 ~30s
─────────────────────────────────────────────────────
Total per video:       ~1 minute            ~5 minutes
```

**First run** downloads models (~4GB): `epiCRealism` SD 1.5 + `AnimateLCM` adapter → `~/.cache/huggingface`  
**Subsequent runs** load from cache — warmup in ~10 seconds

## Troubleshooting

**"MPS not available"**
- MPS only works natively on Apple Silicon (not in Docker)
- Docker on Mac uses CPU — expected behavior

**"Model download stuck"**
- Check internet connection
- Delete partial downloads: `rm -rf ~/.cache/huggingface/hub/`
- Restart backend

**"Frontend can't reach backend"**
- Ensure backend is running: `docker ps`
- Test: `curl http://localhost:8000/`

**"name already in use" on docker run**
- Previous container still exists: `docker rm ai-video-backend`
- Then run the `docker run` command again

## Limitations

- Generation is slow on CPU (~3-5 min per video)
- SD 1.5 quality is lower than SDXL, but at the correct native resolution (512×512)
- AnimateDiff may produce slow or repetitive motion — prompt for dynamic actions helps
- One generation at a time (CPU-bound, single worker)

## Future Work

- Real video animation (Stable Video Diffusion, once GPU available)
- IP-Adapter for reference image style conditioning
- LoRA fine-tuning for consistent styles
- Local database for generation history

## License

- [Diffusers](https://github.com/huggingface/diffusers) (Apache 2.0)
- [FastAPI](https://github.com/tiangolo/fastapi) (MIT)
- [Next.js](https://github.com/vercel/next.js) (MIT)
