import os
import sys
import shutil
import tempfile
from pathlib import Path
from io import BytesIO
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import torch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, UPLOAD_DIR, OUTPUT_DIR
from models import model_cache


@pytest.fixture
def test_client():
    """FastAPI TestClient for API testing"""
    return TestClient(app)


@pytest.fixture
def cleanup_jobs():
    """Clear jobs dictionary before and after each test"""
    from app import jobs
    jobs.clear()
    yield
    jobs.clear()


@pytest.fixture
def sample_image():
    """Create a simple test image (PNG)"""
    img = Image.new("RGB", (512, 512), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def sample_images():
    """Create multiple test images"""
    images = []
    colors = ["red", "green", "blue"]
    for color in colors:
        img = Image.new("RGB", (512, 512), color=color)
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        images.append(img_bytes)
    return images


@pytest.fixture
def cleanup_dirs():
    """Clean up upload and output directories before and after tests"""
    yield
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def mps_available():
    """Check if MPS is available on this system"""
    return torch.backends.mps.is_available()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ["UPLOAD_DIR"] = str(UPLOAD_DIR)
    os.environ["OUTPUT_DIR"] = str(OUTPUT_DIR)
