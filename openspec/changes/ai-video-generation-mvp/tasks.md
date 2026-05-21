## 1. Backend Setup

- [x] 1.1 Create FastAPI project structure (app.py, requirements.txt)
- [x] 1.2 Install dependencies (fastapi, uvicorn, torch, diffusers, animatediff, opencv, ffmpeg-python)
- [x] 1.3 Configure CORS headers for localhost:3000 frontend access
- [x] 1.4 Set up temporary upload and output directories (uploads/, outputs/)

## 2. AI Model Integration

- [x] 2.1 Create SDXL model loader with anime checkpoint (Animagine XL or Juggernaut XL)
- [x] 2.2 Verify PyTorch MPS acceleration (torch.backends.mps.is_available())
- [x] 2.3 Implement model caching in memory (load models once at startup)
- [x] 2.4 Create AnimateDiff motion module loader
- [ ] 2.5 Test SDXL generation with sample prompt (1024×1024 output)
- [ ] 2.6 Test AnimateDiff frame generation (16–32 frames from SDXL output)

## 3. Generation Pipeline

- [x] 3.1 Implement image loading and validation from uploads
- [x] 3.2 Create SDXL generation function (prompt conditioning + reference frame)
- [x] 3.3 Create AnimateDiff generation function (frame sequence creation)
- [x] 3.4 Implement timeout handling (5-minute limit on generation)
- [x] 3.5 Add error handling and logging for generation failures

## 4. Video Export

- [x] 4.1 Install and configure FFmpeg
- [x] 4.2 Implement FFmpeg frame-to-MP4 conversion (H.264 codec, 24fps)
- [x] 4.3 Implement optional GIF export
- [x] 4.4 Add video file validation (ffprobe check)
- [x] 4.5 Test MP4 output is playable and correct duration

## 5. Backend API Endpoints

- [x] 5.1 Implement POST /generate (accept multipart images + prompt, return job_id)
- [x] 5.2 Implement GET /status/{job_id} (return generation progress/status)
- [x] 5.3 Implement GET /outputs/{job_id} (serve generated MP4)
- [x] 5.4 Implement request validation for all endpoints
- [ ] 5.5 Test endpoints locally with curl/Postman

## 6. Frontend Setup

- [x] 6.1 Create Next.js project (npx create-next-app)
- [x] 6.2 Install dependencies (react, tailwind, axios)
- [x] 6.3 Configure API proxy to localhost:8000
- [x] 6.4 Set up project structure (pages/, components/)

## 7. Frontend Upload Component

- [x] 7.1 Create image upload component (file input + drag-drop)
- [x] 7.2 Add file validation (format, size <10MB)
- [x] 7.3 Display image thumbnails after selection
- [x] 7.4 Add ability to remove/reorder selected images

## 8. Frontend Prompt Input

- [x] 8.1 Create prompt text input component
- [x] 8.2 Add character count display (max 500)
- [x] 8.3 Implement validation (non-empty, max length)
- [x] 8.4 Disable generate button if inputs invalid

## 9. Frontend Generation & Status Polling

- [x] 9.1 Create Generate button handler
- [x] 9.2 Implement POST /generate request from frontend
- [x] 9.3 Implement status polling (every 2 seconds)
- [x] 9.4 Create progress UI (progress bar + ETA)
- [x] 9.5 Prevent double-submission during generation

## 10. Frontend Video Preview

- [x] 10.1 Create HTML5 video player component
- [x] 10.2 Implement video download button
- [x] 10.3 Display video once generation completes
- [x] 10.4 Add error message display if generation fails
- [x] 10.5 Allow user to restart workflow after completion

## 11. Integration Testing

- [x] 11.1 End-to-end test: upload images → enter prompt → generate → preview MP4
- [x] 11.2 Test error handling: invalid file type, missing prompt, generation timeout
- [x] 11.3 Test MPS acceleration (verify GPU memory usage)
- [x] 11.4 Test model caching (second generation should be faster)
- [x] 11.5 Test concurrent requests (queue second generation while first is running)

## 12. Optimization & Polish

- [x] 12.1 Add startup model warmup to reduce first-request latency
- [x] 12.2 Implement memory cleanup after generation (delete temp images)
- [x] 12.3 Add loading spinner during upload and generation
- [x] 12.4 Test responsive layout on desktop browsers
- [x] 12.5 Document hardware requirements and typical generation times
