## Context

Building a local AI video generation system on M3 Mac (18GB RAM) for 3–5 second anime clips. The system orchestrates open-source generative models (SDXL, AnimateDiff) without external APIs or microservices.

Current state: architecture documented in IDEA.md, no implementation yet. Target: 2-hour MVP.

## Goals / Non-Goals

**Goals:**
- Generate temporally coherent 3–5 second anime video clips from user-uploaded reference images and text prompts
- Learn full-stack generative AI workflows: model orchestration, prompt engineering, local inference
- Provide a functional UI for upload → generate → preview → export workflow
- Optimize inference for Apple Silicon (MPS acceleration)

**Non-Goals:**
- Identity/character consistency across clips
- LoRA training, ControlNet, or IP-Adapter integration (phase 2+)
- Multi-character composition or story continuity
- Cloud deployment, scaling, or external APIs
- Real-time generation or streaming output

## Decisions

**1. Frontend Framework: Next.js**
- *Decision*: Use Next.js (not plain React or Vue)
- *Rationale*: API routes allow backend logic co-location; serverless-ready for future cloud deployment; strong TypeScript support; modern DX
- *Alternative*: Plain React + separate Node server (more boilerplate, loose coupling)

**2. Backend Framework: FastAPI**
- *Decision*: Use FastAPI (not Django, Flask, or Node.js)
- *Rationale*: Native async/await for long-running generation tasks; pydantic validation for model I/O; integrates naturally with Python AI libraries
- *Alternative*: Flask (simpler but synchronous); Node.js (creates language split with AI layer)

**3. AI Core: Diffusers + AnimateDiff + Anime SDXL**
- *Decision*: Use HuggingFace Diffusers pipeline for SDXL + AnimateDiff motion modules
- *Rationale*: Industry-standard, well-documented, supports local inference; AnimateDiff adds temporal coherence without training
- *Alternative*: ComfyUI (faster experimentation but harder to integrate with APIs); Stable Video Diffusion (lower-quality output, less anime tuning available)
- *Model Choice*: Animagine XL or Juggernaut XL for anime aesthetic
- *Rationale*: These checkpoints are fine-tuned for anime/illustration style and produce higher-quality results than base SDXL

**4. Video Assembly: FFmpeg**
- *Decision*: Use FFmpeg for frame-to-video conversion
- *Rationale*: Production-grade, fast, widely available; mature codec support (H.264, VP9)
- *Alternative*: OpenCV or imageio (higher-level but less control over encoding)

**5. Hardware Acceleration: PyTorch MPS**
- *Decision*: Target Apple Silicon MPS backend for inference
- *Rationale*: M3 Mac has unified memory; MPS offloads compute to GPU efficiently
- *Setup*: Verify `torch.backends.mps.is_available()` at startup

**6. API Design: Simple Request/Response Pattern**
- *Decision*: POST `/generate` with image + prompt, status polling via `/status/{job_id}`, retrieve results via `/outputs/{job_id}`
- *Rationale*: Keeps MVP simple; allows async generation without WebSocket complexity
- *Alternative*: WebSocket streaming (more complex, overkill for 2-hour MVP)

**7. Containerization: Docker for Backend Only**
- *Decision*: FastAPI backend runs in Docker; Next.js frontend runs locally on host
- *Rationale*: Docker isolates Python/model dependencies (PyTorch, Diffusers, AnimateDiff); frontend development benefits from hot reload. Avoids complexity of orchestrating both services in Docker Compose for MVP.
- *Setup*: `docker build -t ai-video-backend .` then `docker run -p 8000:8000 ai-video-backend`
- *Alternative*: Both in Docker Compose (cleaner but more setup overhead); no Docker (works but harder to reproduce across machines)

**8. Model Download Strategy: Automatic at Startup**
- *Decision*: Backend downloads SDXL + AnimateDiff models from Hugging Face at startup via `diffusers` library
- *Rationale*: Single `docker run` command gets everything; no manual setup. Models cached in Docker volume to avoid re-downloading.
- *Implementation*: Backend startup script checks model cache, downloads if missing, reports progress/errors
- *Fallback*: If download fails (offline), backend logs error and exits with helpful message
- *Cache*: Use Docker volume mount for `~/.cache/huggingface/` to persist models across container restarts

**9. Environment Variables**
- `MODEL_CHECKPOINT`: Anime SDXL model identifier (default: `"Animagine/Animagine-XL-3.0"`)
- `HF_HOME`: Hugging Face cache directory (default: `/root/.cache/huggingface/` in container)
- `UPLOAD_DIR`: Temporary image upload directory (default: `/tmp/uploads/`)
- `OUTPUT_DIR`: Generated video output directory (default: `/outputs/`)
- `DEVICE`: Compute device (default: `"mps"` on macOS, fallback to `"cpu"`)

**10. Git & Repository**
- *Decision*: Initialize git with `.gitignore` excluding generated videos, model caches, and temp files
- *Ignored*: `outputs/`, `uploads/`, `.cache/`, `*.mp4`, `*.gif`, Python virtual environments, node_modules
- *Rationale*: Keep repo focused on code; generated artifacts are transient; model caches are large and pulled fresh on startup

## Risks / Trade-offs

**[Inference Speed]** → Local generation of 16–32 AnimateDiff frames may take 2–5 minutes per clip on M3 Mac
- *Mitigation*: Set user expectations; implement async status polling; show progress indicators in UI

**[VRAM Constraints]** → Loading SDXL + AnimateDiff modules consumes ~12GB; no simultaneous generations
- *Mitigation*: Queue requests; load models once, cache in memory; document hardware requirements

**[Temporal Incoherence]** → AnimateDiff alone doesn't guarantee multi-frame consistency; may see flickering or jitter
- *Mitigation*: Keep clips short (3–5s); anime style masks artifacts; defer advanced techniques (ControlNet, IP-Adapter) to phase 2

**[No Authentication]** → MVP has no user isolation or session management
- *Mitigation*: Acceptable for local/single-user; add later if needed

**[Synchronous Model Loading]** → First request to `/generate` blocks while loading models; subsequent requests fast
- *Mitigation*: Warm up models on backend startup; document first-request latency in UI
