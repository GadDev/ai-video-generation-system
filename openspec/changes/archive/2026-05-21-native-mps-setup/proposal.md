## Why

The backend currently runs inside Docker, which has no access to Apple Silicon MPS (Metal Performance Shaders). Running natively on macOS gives PyTorch direct GPU access, reducing AnimateLCM generation time from ~5 minutes to ~30-60 seconds — a 5-10x speedup with zero code changes to the AI pipeline.

## What Changes

- **Remove**: Docker-based backend setup (Dockerfile, docker-compose.yml usage for dev)
- **Add**: Native Python virtual environment setup for backend (`backend/venv`)
- **Add**: `backend/run.sh` — one-command startup script that activates venv and starts uvicorn
- **Modify**: `models.py` — device selection already supports MPS (`"mps" if torch.backends.mps.is_available() else "cpu"`), but Docker forced CPU; native run will auto-detect MPS
- **Modify**: `STARTUP.md` — replace Docker instructions with native venv setup
- **Modify**: `README.md` — update architecture, prerequisites, and generation timeline
- **Keep**: Dockerfile (useful for non-Mac deployments and CI), just not the primary dev path

## Capabilities

### New Capabilities

- `native-backend-setup`: Native Python venv setup and startup for the backend with MPS auto-detection

### Modified Capabilities

- (none — no spec-level behavior changes, only runtime environment changes)

## Impact

- `backend/models.py`: MPS branch now active (`DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"`)
- `backend/requirements.txt`: Needs macOS-compatible torch (MPS-enabled builds ship in standard PyTorch ≥ 2.0)
- `STARTUP.md`, `README.md`: Primary setup path changes from Docker to native venv
- No API, frontend, or generation logic changes
