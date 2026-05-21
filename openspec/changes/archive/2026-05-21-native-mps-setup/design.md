## Context

The backend currently runs in Docker on macOS. Docker's Linux VM has no access to Apple Silicon GPU (MPS). This forces all PyTorch inference to CPU, making AnimateLCM generation ~5 minutes per video. Running the same code natively on macOS gives PyTorch direct MPS access, with no changes to the AI pipeline code — `models.py` already has `DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"` but this branch never executes inside Docker.

The frontend (Next.js) is already running natively and is unaffected.

## Goals / Non-Goals

**Goals:**
- Native venv setup that activates MPS automatically on Apple Silicon
- Single-command startup (`./backend/run.sh`)
- Keep Dockerfile intact for non-Mac environments
- Update docs to make native path the primary dev workflow

**Non-Goals:**
- Removing Docker entirely (keep it for CI, non-Mac deployments)
- GPU memory tuning or MPS-specific optimizations
- Changing any AI pipeline, API, or frontend code

## Decisions

### Virtual environment location: `backend/venv/`

Keeps the venv co-located with the backend code. `.gitignore` already covers `venv/`. Alternative (global pyenv/conda) was rejected — too much user environment variance, harder to reproduce.

### PyTorch install: standard PyPI build

`torch==2.1.1` from PyPI ships with MPS support on macOS. No separate install URL needed (unlike CUDA which requires `--index-url`). MPS is auto-detected at runtime.

### Startup script: `backend/run.sh`

Single file that:
1. Creates venv if it doesn't exist
2. Activates venv
3. Installs requirements if needed
4. Starts uvicorn on port 8000

This replaces the `docker run` command as the primary startup method. Keeps the same port (8000) so the frontend needs no changes.

### `OPENBLAS_NUM_THREADS=1` kept

Already in Dockerfile ENV. Needs to be set in `run.sh` as well to suppress OpenBLAS threading warnings on macOS.

## Risks / Trade-offs

- **[Risk] Dependency conflicts with system Python** → Mitigation: always use venv, never system Python
- **[Risk] MPS not available on Intel Macs** → Mitigation: `models.py` already falls back to CPU; no crash, just slower
- **[Risk] First-time install takes ~5 min** → Mitigation: document this clearly; subsequent starts are instant
- **[Trade-off] Dockerfile no longer tested in dev** → Acceptable for local dev; CI can validate Docker path separately

## Migration Plan

1. Add `backend/run.sh` startup script
2. Add `backend/venv/` to `.gitignore` (if not already present)
3. Update `STARTUP.md` — native path becomes primary, Docker becomes "alternative"
4. Update `README.md` — prerequisites, quick start, generation timeline
5. No rollback needed — Docker path unchanged, just demoted in docs
