"""
Test cancel/stop generation feature
"""
import time
import pytest


@pytest.mark.asyncio
async def test_cancel_generation(test_client, cleanup_jobs, cleanup_dirs):
    """Test that generation can be cancelled while in progress"""
    prompt = "A beautiful landscape"

    # Start generation
    response = test_client.post(
        "/generate",
        data={"prompt": prompt},
        files=[]
    )

    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # Give it a moment to start processing
    time.sleep(0.5)

    # Cancel the generation
    cancel_response = test_client.delete(f"/generate/{job_id}")
    assert cancel_response.status_code == 200
    cancel_data = cancel_response.json()
    assert cancel_data["status"] == "cancelled"

    # Verify status shows cancelled
    status_response = test_client.get(f"/status/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_nonexistent_job(test_client, cleanup_jobs):
    """Test that cancelling non-existent job returns 404"""
    response = test_client.delete("/generate/nonexistent-job-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_cancel_completed_job(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that completed jobs cannot be cancelled"""
    sample_image.seek(0)
    files = [("images", ("test.png", sample_image, "image/png"))]

    # Start and wait for completion
    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=files
    )

    job_id = response.json()["job_id"]

    # Mark as complete manually (simulating completion)
    from app import jobs
    jobs[job_id]["status"] = "complete"

    # Try to cancel - should fail
    cancel_response = test_client.delete(f"/generate/{job_id}")
    assert cancel_response.status_code == 400
    error = cancel_response.json()
    assert "error" in error


@pytest.mark.asyncio
async def test_cancel_then_poll_status(test_client, cleanup_jobs, cleanup_dirs):
    """Test that status polling works correctly after cancellation"""
    response = test_client.post(
        "/generate",
        data={"prompt": "Test cancellation flow"},
        files=[]
    )

    job_id = response.json()["job_id"]
    time.sleep(0.5)

    # Cancel
    test_client.delete(f"/generate/{job_id}")

    # Poll status multiple times
    for _ in range(3):
        status_response = test_client.get(f"/status/{job_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "cancelled"
        time.sleep(0.1)
