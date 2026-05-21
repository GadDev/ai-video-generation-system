## 1. Native Startup Script

- [x] 1.1 Create `backend/run.sh` — creates venv if missing, installs requirements, sets `OPENBLAS_NUM_THREADS=1`, starts uvicorn on port 8000
- [x] 1.2 Make `backend/run.sh` executable (`chmod +x`)
- [x] 1.3 Add `backend/venv/` to `.gitignore`

## 2. Update models.py for MPS

- [x] 2.1 Verify `DEVICE` selection in `models.py` correctly uses `"mps"` when available (currently set to `"cpu"` hardcoded — fix to auto-detect)
- [x] 2.2 Update `torch_dtype` handling: use `torch.float16` for MPS, `torch.float32` for CPU

## 3. Update Documentation

- [x] 3.1 Rewrite `STARTUP.md` — native venv path is primary, Docker becomes "Alternative (non-Mac)"
- [x] 3.2 Update `README.md` prerequisites (Python 3.11+ instead of Docker Desktop as primary)
- [x] 3.3 Update `README.md` Quick Start to use `./backend/run.sh` instead of `docker run`
- [x] 3.4 Update `README.md` generation timeline to reflect MPS speeds (~30-60s per video)

## 4. Verify

- [x] 4.1 Run `./backend/run.sh` and confirm logs show `Using device: mps`
- [ ] 4.2 Submit a test generation and confirm it completes faster than Docker/CPU baseline
