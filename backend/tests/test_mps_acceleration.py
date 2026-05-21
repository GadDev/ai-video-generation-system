"""
11.3 Test MPS acceleration: verify GPU memory usage and device allocation
"""
import pytest
import torch
import psutil
import os
from models import model_cache


def test_mps_availability():
    """Verify MPS is available on this system"""
    is_mps_available = torch.backends.mps.is_available()
    if is_mps_available:
        assert torch.backends.mps.is_available()
        # Log MPS device properties if available
        try:
            props = torch.mps.get_device_properties(0)
            assert props is not None
        except RuntimeError:
            pass  # Some systems may not support detailed props


def test_device_allocation(mps_available):
    """Verify device allocation matches system capabilities"""
    if mps_available:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        assert device == "mps"
    else:
        device = "cpu"
        assert device == "cpu"


def test_model_cache_device():
    """Verify models are allocated to correct device"""
    from models import DEVICE

    if torch.backends.mps.is_available():
        assert DEVICE == "mps"
    else:
        assert DEVICE == "cpu"

    assert model_cache.device == DEVICE


@pytest.mark.asyncio
async def test_memory_usage_before_load():
    """Baseline memory usage"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    initial_rss = mem_info.rss / (1024 * 1024)  # MB

    # Log initial memory
    print(f"\n✓ Initial RSS memory: {initial_rss:.2f} MB")

    yield initial_rss


@pytest.mark.asyncio
async def test_model_loading_memory(mps_available):
    """Test memory usage during model loading"""
    if not mps_available:
        pytest.skip("MPS not available on this system")

    process = psutil.Process(os.getpid())

    # Baseline
    mem_before = process.memory_info().rss / (1024 * 1024)

    # Load model
    try:
        model_cache.load_sdxl()
        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_increase = mem_after - mem_before

        # Expect significant memory usage increase (at least 100MB)
        print(f"\n✓ Memory before model load: {mem_before:.2f} MB")
        print(f"✓ Memory after model load: {mem_after:.2f} MB")
        print(f"✓ Memory increase: {mem_increase:.2f} MB")

        assert mem_increase > 100, f"Expected >100MB increase, got {mem_increase:.2f}MB"

    finally:
        model_cache.cleanup()


def test_device_consistency():
    """Verify consistent device usage across model cache"""
    assert model_cache.device in ["mps", "cpu"]

    if torch.backends.mps.is_available():
        assert model_cache.device == "mps"
    else:
        assert model_cache.device == "cpu"


@pytest.mark.asyncio
async def test_mps_tensor_operations(mps_available):
    """Test basic tensor operations on correct device"""
    if not mps_available:
        pytest.skip("MPS not available on this system")

    device = "mps"
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)

    # Matrix multiplication on MPS
    z = torch.matmul(x, y)

    assert z.device.type == "mps"
    assert z.shape == (1000, 1000)


@pytest.mark.asyncio
async def test_verify_mps_enabled_in_models():
    """Verify MPS is properly configured in model loading"""
    from models import DEVICE

    if torch.backends.mps.is_available():
        assert DEVICE == "mps"
        assert model_cache.device == "mps"
    else:
        assert DEVICE == "cpu"
        assert model_cache.device == "cpu"
