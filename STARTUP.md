# Quick Start Guide

## Step 1: Start Backend (Native — Apple Silicon recommended)

```bash
cd ai-video-generation-system
./backend/run.sh
```

This script:
1. Creates a Python venv at `backend/venv/` (first time only)
2. Installs all dependencies (first time only, ~5 min)
3. Auto-detects MPS on Apple Silicon
4. Starts the backend on `http://localhost:8000`

Wait for:
```
INFO:models:Using device: mps
INFO:models:✓ AnimateDiff + LCM pipeline loaded successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> **Subsequent starts:** Just run `./backend/run.sh` again — venv and models are cached.

## Step 2: Start Frontend (New Terminal)

```bash
cd frontend
npm install    # Only needed once
npm run dev
```

Frontend ready at **`http://localhost:3000`**

## Step 3: Generate Your First Video

1. Open http://localhost:3000
2. **Optional**: Drag/drop 1-5 reference images
3. **Required**: Enter a prompt (e.g., `"cat dancing under the moon, anime style"`)
4. Click **"Generate Video"**
5. Watch the progress bar — expect **30-60 seconds on Apple Silicon MPS**
6. **Cancel anytime** with the red button
7. Download MP4 when complete

## Performance

| Stage | Apple Silicon MPS | CPU (no GPU) |
|-------|-------------------|--------------|
| First startup (model download) | ~5 min | ~5 min |
| AnimateLCM (6 steps, 16 frames) | 30-60s | 3-5 min |
| Export + validation | ~15s | ~30s |
| **Total (after first run)** | **~1 min** | **~5 min** |

## Cheat Sheet

```bash
# Start backend
./backend/run.sh

# Start frontend (separate terminal)
cd frontend && npm run dev

# Test backend is running
curl http://localhost:8000/

# Submit a test generation
curl -X POST http://localhost:8000/generate -F "prompt=beautiful sunset"

# Check status
curl http://localhost:8000/status/{job_id}

# View backend logs (separate terminal)
# Logs print directly to the terminal where run.sh is running
```

## Troubleshooting

**`python3: command not found`**
- Install Python 3.11+: `brew install python@3.11`
- Or use pyenv: `pyenv install 3.11`

**`MPS not available` in logs**
- Expected on Intel Macs — falls back to CPU automatically
- On Apple Silicon: ensure macOS 12.3+ and PyTorch 2.0+

**Port 8000 already in use**
```bash
lsof -i :8000          # Find what's using the port
kill -9 <PID>          # Kill it
./backend/run.sh        # Restart
```

**Dependencies fail to install**
```bash
rm -rf backend/venv    # Delete venv
./backend/run.sh        # Recreate from scratch
```

**Generation stuck for more than 5 minutes**
- Check terminal output where `run.sh` is running
- Press `Ctrl+C` to stop, then restart with `./backend/run.sh`

---

## Alternative: Docker (non-Mac or CI)

If you're not on macOS or want containerized deployment:

```bash
# Build
cd backend && docker build -t ai-video-backend .

# First time
docker run --name ai-video-backend -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(pwd)/outputs:/outputs" \
  ai-video-backend

# Subsequent times
docker stop ai-video-backend
docker start ai-video-backend
```

> Note: Docker on Mac uses CPU (no MPS access). Use native `run.sh` for full speed.
