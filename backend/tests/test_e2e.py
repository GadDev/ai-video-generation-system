"""
End-to-end integration test: upload images → enter prompt → generate → preview MP4
"""
import time
import pytest
from pathlib import Path
from app import OUTPUT_DIR


@pytest.mark.asyncio
async def test_e2e_full_workflow(test_client, sample_images, cleanup_jobs, cleanup_dirs):
    """
    11.1 End-to-end test: upload images → enter prompt → generate → preview MP4

    Verifies:
    - Image upload succeeds
    - Prompt validation works
    - Job creation and status polling
    - MP4 generation and download
    """
    prompt = "A beautiful anime character standing in a cyberpunk city"

    # Reset file pointers for images
    for img in sample_images:
        img.seek(0)

    # Step 1: Upload images and prompt
    files = [
        ("images", ("image1.png", sample_images[0], "image/png")),
        ("images", ("image2.png", sample_images[1], "image/png")),
        ("images", ("image3.png", sample_images[2], "image/png")),
    ]

    response = test_client.post(
        "/generate",
        data={"prompt": prompt},
        files=files
    )

    assert response.status_code == 200, f"Failed to create generation job: {response.text}"
    job_data = response.json()
    assert "job_id" in job_data
    job_id = job_data["job_id"]

    # Step 2: Poll status until completion or timeout
    max_wait = 300  # 5 minutes timeout
    poll_interval = 1  # 1 second between polls
    start_time = time.time()

    job_complete = False
    while time.time() - start_time < max_wait:
        status_response = test_client.get(f"/status/{job_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert "status" in status_data

        if status_data["status"] == "complete":
            job_complete = True
            assert status_data["progress"] == 100
            assert status_data["output_url"] == f"/outputs/{job_id}"
            break
        elif status_data["status"] == "failed":
            pytest.fail(f"Generation failed: {status_data.get('message', 'Unknown error')}")

        time.sleep(poll_interval)

    assert job_complete, f"Job did not complete within {max_wait} seconds"

    # Step 3: Download generated MP4
    output_response = test_client.get(f"/outputs/{job_id}")
    assert output_response.status_code == 200
    assert output_response.headers["content-type"] == "video/mp4"

    # Step 4: Verify MP4 is valid
    mp4_path = OUTPUT_DIR / f"{job_id}.mp4"
    assert mp4_path.exists(), f"MP4 file not found at {mp4_path}"

    # Verify file size is reasonable (at least 1KB)
    file_size = mp4_path.stat().st_size
    assert file_size > 1024, f"MP4 file is too small: {file_size} bytes"


@pytest.mark.asyncio
async def test_generate_endpoint_invalid_prompt(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that empty prompt is rejected"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": ""},
        files=files
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_generate_endpoint_no_images(test_client, cleanup_jobs, cleanup_dirs):
    """Test that generation requires at least one image"""
    response = test_client.post(
        "/generate",
        data={"prompt": "A nice landscape"},
        files=[]
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_status_nonexistent_job(test_client, cleanup_jobs):
    """Test that querying nonexistent job returns 404"""
    response = test_client.get("/status/nonexistent-job-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_output_not_ready(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that output endpoint returns 202 while job is in progress"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=files
    )

    job_id = response.json()["job_id"]

    # Immediately try to get output (should not be ready)
    output_response = test_client.get(f"/outputs/{job_id}")
    # Status could be 202 (not ready) or processing might be instant in tests
    assert output_response.status_code in [202, 404]
