## ADDED Requirements

### Requirement: Native startup script
The system SHALL provide a `backend/run.sh` script that sets up and starts the backend without Docker.

#### Scenario: First run — venv does not exist
- **WHEN** user runs `./backend/run.sh` for the first time
- **THEN** script creates `backend/venv/`, installs all requirements, and starts uvicorn on port 8000

#### Scenario: Subsequent run — venv already exists
- **WHEN** user runs `./backend/run.sh` and `backend/venv/` already exists
- **THEN** script skips installation and starts uvicorn directly

#### Scenario: MPS available
- **WHEN** backend starts on Apple Silicon Mac
- **THEN** `models.py` logs `Using device: mps` and all inference runs on MPS

#### Scenario: MPS not available
- **WHEN** backend starts on Intel Mac or Linux
- **THEN** `models.py` logs `Using device: cpu` and falls back to CPU inference without error

### Requirement: Gitignore excludes venv
The repository SHALL NOT track the native venv directory.

#### Scenario: venv not committed
- **WHEN** `backend/venv/` is created by `run.sh`
- **THEN** `git status` does not show `backend/venv/` as an untracked file

### Requirement: Docker path remains functional
The Dockerfile and docker-compose.yml SHALL remain valid and buildable for non-Mac deployments.

#### Scenario: Docker build still works
- **WHEN** user runs `docker build -t ai-video-backend backend/`
- **THEN** build completes without error
