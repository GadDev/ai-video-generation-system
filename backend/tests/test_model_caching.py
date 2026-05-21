"""
11.4 Test model caching: second generation should be faster than first
"""
import time
import pytest
from app import model_cache


@pytest.mark.asyncio
async def test_model_cache_hits():
    """Test that models are cached after first load"""
    # Reset cache
    model_cache.cleanup()
    assert model_cache.sdxl_pipeline is None

    # First load
    start = time.time()
    pipeline = model_cache.load_sdxl()
    first_load_time = time.time() - start

    assert pipeline is not None
    assert model_cache.sdxl_pipeline is not None
    print(f"\n✓ First SDXL load: {first_load_time:.2f}s")

    # Second load (should be instant cache hit)
    start = time.time()
    pipeline2 = model_cache.load_sdxl()
    second_load_time = time.time() - start

    assert pipeline2 is pipeline  # Same object in memory
    assert second_load_time < 0.1  # Should be nearly instant
    print(f"✓ Second SDXL load (cached): {second_load_time:.4f}s")

    # Verify caching reduced load time
    assert second_load_time < first_load_time


@pytest.mark.asyncio
async def test_model_cache_state():
    """Test that model cache maintains state across calls"""
    model_cache.cleanup()

    # Load model
    model_cache.load_sdxl()
    cached_ref = model_cache.sdxl_pipeline

    # Load again without reloading
    model_cache.load_sdxl()
    cached_ref2 = model_cache.sdxl_pipeline

    # Should be the same object
    assert cached_ref is cached_ref2
    print(f"\n✓ Model cache maintains object identity across loads")


@pytest.mark.asyncio
async def test_concurrent_cache_access():
    """Test that concurrent access to cached models works correctly"""
    import asyncio

    model_cache.cleanup()

    async def load_model():
        start = time.time()
        pipeline = model_cache.load_sdxl()
        elapsed = time.time() - start
        return pipeline, elapsed

    # First load
    pipeline1, time1 = await load_model()
    print(f"\n✓ First load: {time1:.2f}s")

    # Concurrent loads
    tasks = [load_model() for _ in range(3)]
    results = await asyncio.gather(*tasks)

    for i, (pipeline, elapsed) in enumerate(results):
        assert pipeline is pipeline1
        assert elapsed < 0.1  # Cached hits
        print(f"✓ Concurrent load {i+1}: {elapsed:.4f}s")


def test_cache_none_when_not_loaded():
    """Test that cache returns None when models not loaded"""
    model_cache.cleanup()

    assert model_cache.sdxl_pipeline is None
    assert model_cache.animatediff_pipeline is None


@pytest.mark.asyncio
async def test_cleanup_clears_cache():
    """Test that cleanup properly clears cached models"""
    # Load model
    model_cache.load_sdxl()
    assert model_cache.sdxl_pipeline is not None

    # Cleanup
    model_cache.cleanup()

    # Should be None
    assert model_cache.sdxl_pipeline is None
    print(f"\n✓ Model cleanup clears pipeline references")
