## Why

Building an AI video generation system teaches full-stack generative AI workflows (model orchestration, prompt engineering, local inference) while producing visually impressive results. A 2-hour MVP targeting 3–5 second anime clips is feasible on an M3 Mac and bridges the gap between experimentation (ComfyUI) and production (custom code).

## What Changes

- **New Frontend** (Next.js): Upload anime reference images, enter generation prompts, preview generated clips
- **New Backend** (FastAPI): Orchestrate SDXL image generation and AnimateDiff motion synthesis
- **New AI Pipeline**: Use Diffusers + AnimateDiff + anime SDXL checkpoint to generate short coherent video clips locally
- **New Video Export**: FFmpeg-based assembly of generated frames into MP4
- **Apple Silicon Optimization**: Leverage MPS acceleration for inference on local M3 Mac

## Capabilities

### New Capabilities
- `image-upload`: Accept 2–5 anime/person reference images from user
- `prompt-input`: Text prompt input for video generation (e.g., "cyberpunk rooftop at sunset")
- `video-generation-pipeline`: SDXL frame generation + AnimateDiff motion synthesis to create 3–5 second clips
- `video-export`: FFmpeg-based MP4 and GIF export from generated frame sequences
- `generation-api`: FastAPI backend to orchestrate upload, generation, and export workflows
- `frontend-preview`: Next.js UI for uploading, prompting, generating, and previewing results

### Modified Capabilities

(None—this is a new system)

## Impact

- **New Dependencies**: Next.js, FastAPI, Diffusers, AnimateDiff, PyTorch, FFmpeg
- **New Code**: Frontend (Next.js), Backend (FastAPI), AI Layer (Python generation pipeline)
- **Hardware**: Requires ~12GB RAM for model inference on Apple Silicon
- **Local-only**: No external APIs or cloud services in MVP scope
