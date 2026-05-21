# Quick Start Guide

## Step 1: Build Backend Image

```bash
cd backend
docker build -t ai-video-backend .
```

Do this once, or when code changes.

## Step 2: Start Backend Container

**First time only:**
```bash
docker run --name ai-video-backend -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(pwd)/outputs:/outputs" \
  ai-video-backend
```

Watch for success message:
```
INFO:models:✓ Model warmup complete
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Backend ready at **`http://localhost:8000`**

**Subsequent times:** Stop and restart (much faster - models cached):
```bash
docker stop ai-video-backend
docker start ai-video-backend
docker logs -f ai-video-backend  # Optional: view logs
```

> **Why this approach?** The `--name` flag creates a reusable container. Cached models stay in `~/.cache/huggingface`, making subsequent starts ~10x faster.

## Step 3: Start Frontend (Separate Terminal)

```bash
cd frontend
npm install    # Only needed once
npm run dev
```

Frontend ready at **`http://localhost:3000`**

## Step 4: Generate Your First Video

1. Open http://localhost:3000
2. **Optional**: Drag/drop 1-5 reference images
3. **Required**: Enter prompt (e.g., `"sunset over mountains, peaceful anime style"`)
4. Click **"Generate Video"**
5. Watch progress bar update (4-6 minutes)
6. **Cancel anytime** with red "Cancel Generation" button
7. Download MP4 when complete

## Performance Notes

- **First request**: +5-10 min (model download on first run)
- **Base generation**: 4-6 min (CPU) / 1-2 min (Apple Silicon MPS)
- **Video output**: 120 frames at 24fps = 5 seconds
- **Video size**: ~50-150MB (depends on content)

## Cheat Sheet

```bash
# === BACKEND ===
# Build image (once)
cd backend && docker build -t ai-video-backend .

# Start container (first time)
docker run --name ai-video-backend -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(pwd)/outputs:/outputs" \
  ai-video-backend

# Stop container
docker stop ai-video-backend

# Restart container (faster - uses cached models)
docker start ai-video-backend

# View logs
docker logs -f ai-video-backend

# === FRONTEND ===
# Install dependencies (once)
cd frontend && npm install

# Start dev server
npm run dev

# === TESTING ===
# Test backend health
curl http://localhost:8000/

# Submit a generation
curl -X POST http://localhost:8000/generate \
  -F "prompt=beautiful sunset"

# Check status
curl http://localhost:8000/status/{job_id}
```

## Troubleshooting

**"docker: command not found"** or container won't start:
- Ensure Docker Desktop is running
- Check port 8000 is free: `lsof -i :8000`
- If port is in use, kill it: `killall -9 python` or restart Docker

**Backend container exits with error**:
- Check logs: `docker logs ai-video-backend`
- If model download failed: `rm -rf ~/.cache/huggingface/` and restart
- Rebuild image: `docker build --no-cache -t ai-video-backend .`
- Ensure 8GB+ Docker memory: Docker Desktop → Preferences → Resources

**Frontend can't reach backend**:
- Verify backend is running: `docker ps` (should show `ai-video-backend`)
- Test directly: `curl http://localhost:8000/`
- Check CORS: Backend should accept `http://localhost:3000`

**Generation times out or hangs**:
- First request is expected to be slow (normal, 5-10 min total)
- Check logs: `docker logs -f ai-video-backend`
- If stuck for >15 min, restart: `docker stop ai-video-backend` then `docker start ai-video-backend`
- Try a shorter prompt or fewer reference images

**Can't restart container: "name already in use"**:
- If previous container crashed: `docker rm ai-video-backend`
- Then start fresh: `docker run --name ai-video-backend ...`

## Next Steps

See README.md for:
- Full API endpoint documentation
- Environment variables & configuration
- Architecture & design details
- Performance optimization tips
