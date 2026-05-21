#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

export OPENBLAS_NUM_THREADS=1
export UPLOAD_DIR="${UPLOAD_DIR:-/tmp/uploads}"
export OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/../outputs}"
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"

mkdir -p "$OUTPUT_DIR" /tmp/uploads "$HF_HOME"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if ! python -c "import fastapi" 2>/dev/null; then
  echo "Installing requirements..."
  pip install --upgrade pip -q
  pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Starting backend (MPS auto-detected if on Apple Silicon)..."
cd "$SCRIPT_DIR"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
