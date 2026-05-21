## 1. Backend Setup

- [ ] 1.1 Create FastAPI project structure (app.py, requirements.txt)
- [ ] 1.2 Install dependencies (fastapi, uvicorn, torch, diffusers, animatediff, opencv, ffmpeg-python)
- [ ] 1.3 Configure CORS headers for localhost:3000 frontend access
- [ ] 1.4 Set up temporary upload and output directories (uploads/, outputs/)

## 2. AI Model Integration

- [ ] 2.1 Create SDXL model loader with anime checkpoint (Animagine XL or Juggernaut XL)
- [ ] 2.2 Verify PyTorch MPS acceleration (torch.backends.mps.is_available())
- [ ] 2.3 Implement model caching in memory (load models once at startup)
- [ ] 2.4 Create AnimateDiff motion module loader
- [ ] 2.5 Test SDXL generation with sample prompt (1024×1024 output)
- [ ] 2.6 Test AnimateDiff frame generation (16–32 frames from SDXL output)

## 3. Generation Pipeline

- [ ] 3.1 Implement image loading and validation from uploads
- [ ] 3.2 Create SDXL generation function (prompt conditioning + reference frame)
- [ ] 3.3 Create AnimateDiff generation function (frame sequence creation)
- [ ] 3.4 Implement timeout handling (5-minute limit on generation)
- [ ] 3.5 Add error handling and logging for generation failures

## 4. Video Export

- [ ] 4.1 Install and configure FFmpeg
- [ ] 4.2 Implement FFmpeg frame-to-MP4 conversion (H.264 codec, 24fps)
- [ ] 4.3 Implement optional GIF export
- [ ] 4.4 Add video file validation (ffprobe check)
- [ ] 4.5 Test MP4 output is playable and correct duration

## 5. Backend API Endpoints

- [ ] 5.1 Implement POST /generate (accept multipart images + prompt, return job_id)
- [ ] 5.2 Implement GET /status/{job_id} (return generation progress/status)
- [ ] 5.3 Implement GET /outputs/{job_id} (serve generated MP4)
- [ ] 5.4 Implement request validation for all endpoints
- [ ] 5.5 Test endpoints locally with curl/Postman

## 6. Frontend Setup

- [ ] 6.1 Create Next.js project (npx create-next-app)
- [ ] 6.2 Install dependencies (react, tailwind, axios)
- [ ] 6.3 Configure API proxy to localhost:8000
- [ ] 6.4 Set up project structure (pages/, components/)

## 7. Frontend Upload Component

- [ ] 7.1 Create image upload component (file input + drag-drop)
- [ ] 7.2 Add file validation (format, size <10MB)
- [ ] 7.3 Display image thumbnails after selection
- [ ] 7.4 Add ability to remove/reorder selected images

## 8. Frontend Prompt Input

- [ ] 8.1 Create prompt text input component
- [ ] 8.2 Add character count display (max 500)
- [ ] 8.3 Implement validation (non-empty, max length)
- [ ] 8.4 Disable generate button if inputs invalid

## 9. Frontend Generation & Status Polling

- [ ] 9.1 Create Generate button handler
- [ ] 9.2 Implement POST /generate request from frontend
- [ ] 9.3 Implement status polling (every 2 seconds)
- [ ] 9.4 Create progress UI (progress bar + ETA)
- [ ] 9.5 Prevent double-submission during generation

## 10. Frontend Video Preview

- [ ] 10.1 Create HTML5 video player component
- [ ] 10.2 Implement video download button
- [ ] 10.3 Display video once generation completes
- [ ] 10.4 Add error message display if generation fails
- [ ] 10.5 Allow user to restart workflow after completion

## 11. Integration Testing

- [ ] 11.1 End-to-end test: upload images → enter prompt → generate → preview MP4
- [ ] 11.2 Test error handling: invalid file type, missing prompt, generation timeout
- [ ] 11.3 Test MPS acceleration (verify GPU memory usage)
- [ ] 11.4 Test model caching (second generation should be faster)
- [ ] 11.5 Test concurrent requests (queue second generation while first is running)

## 12. Optimization & Polish

- [ ] 12.1 Add startup model warmup to reduce first-request latency
- [ ] 12.2 Implement memory cleanup after generation (delete temp images)
- [ ] 12.3 Add loading spinner during upload and generation
- [ ] 12.4 Test responsive layout on desktop browsers
- [ ] 12.5 Document hardware requirements and typical generation times
