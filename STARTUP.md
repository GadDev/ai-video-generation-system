# Quick Start Guide

## Start Backend (Docker)

```bash
cd backend
docker build -t ai-video-backend .
docker run -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v $(pwd)/outputs:/outputs \
  ai-video-backend
```

Watch for:
```
✓ PyTorch MPS acceleration available
✓ Model warmup complete
```

Backend ready at `http://localhost:8000`

## Start Frontend (Separate Terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend ready at `http://localhost:3000`

## First Test

1. Go to http://localhost:3000
2. Upload 2-3 anime images (JPEG/PNG)
3. Enter prompt: `"anime sunset scenery, peaceful"`
4. Click "Generate Video"
5. Wait 2-3 minutes (watch progress)
6. Download MP4

## Performance Notes

- **First request**: 2-3 minutes (model loading)
- **Subsequent**: 1-2 minutes (models cached)
- **Video output**: 3-5 seconds at 24fps
- **Storage**: Each video ~50-200MB

## Troubleshooting

**Backend won't start**:
- Check Docker is running
- Verify port 8000 is free
- Check internet for model download

**Frontend can't reach backend**:
- Ensure backend is running on :8000
- Check browser console for CORS errors
- Try http://localhost:8000 directly

**Generation timeout**:
- First request takes longer (model warmup)
- Check Docker container logs for errors

## Next: Run Integration Tests

After verifying basic workflow works:

```bash
# Test 1: Different prompts
# Test 2: Multiple uploads
# Test 3: Concurrent generations (start 2nd while 1st is running)
# Test 4: Check outputs/ folder for generated videos
```

See README.md for full API documentation.
