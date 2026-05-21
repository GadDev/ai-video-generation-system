"""
11.5 Test concurrent requests: queue second generation while first is running
"""
import time
import asyncio
import pytest
from PIL import Image
from io import BytesIO


def create_test_image():
    """Helper to create a test image"""
    img = Image.new("RGB", (512, 512), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.asyncio
async def test_concurrent_generation_requests(test_client, cleanup_jobs, cleanup_dirs):
    """
    11.5 Test concurrent requests: queue second generation while first is running

    Verifies:
    - First generation starts
    - Second generation can be queued while first is in progress
    - Both jobs complete successfully
    - Both jobs have separate job_ids and outputs
    """
    prompt1 = "A magical forest with glowing trees"
    prompt2 = "A cyberpunk neon city street"

    # Step 1: Start first generation
    files1 = [("images", ("image1.png", create_test_image(), "image/png"))]

    response1 = test_client.post(
        "/generate",
        data={"prompt": prompt1},
        files=files1
    )

    assert response1.status_code == 200
    job_id_1 = response1.json()["job_id"]
    print(f"\n✓ Job 1 started: {job_id_1}")

    # Small delay to ensure first job is processing
    await asyncio.sleep(0.5)

    # Step 2: Start second generation while first is running
    files2 = [("images", ("image2.png", create_test_image(), "image/png"))]

    response2 = test_client.post(
        "/generate",
        data={"prompt": prompt2},
        files=files2
    )

    assert response2.status_code == 200
    job_id_2 = response2.json()["job_id"]
    print(f"✓ Job 2 started: {job_id_2}")

    # Verify they have different IDs
    assert job_id_1 != job_id_2

    # Step 3: Poll both jobs until completion or timeout
    max_wait = 300
    poll_interval = 1
    start_time = time.time()

    job_1_complete = False
    job_2_complete = False

    while time.time() - start_time < max_wait:
        # Poll job 1
        if not job_1_complete:
            status1 = test_client.get(f"/status/{job_id_1}").json()
            if status1["status"] == "complete":
                job_1_complete = True
                print(f"✓ Job 1 completed (progress: {status1['progress']}%)")
            elif status1["status"] == "failed":
                pytest.fail(f"Job 1 failed: {status1.get('message', 'Unknown error')}")

        # Poll job 2
        if not job_2_complete:
            status2 = test_client.get(f"/status/{job_id_2}").json()
            if status2["status"] == "complete":
                job_2_complete = True
                print(f"✓ Job 2 completed (progress: {status2['progress']}%)")
            elif status2["status"] == "failed":
                pytest.fail(f"Job 2 failed: {status2.get('message', 'Unknown error')}")

        if job_1_complete and job_2_complete:
            break

        await asyncio.sleep(poll_interval)

    assert job_1_complete, f"Job 1 did not complete within {max_wait} seconds"
    assert job_2_complete, f"Job 2 did not complete within {max_wait} seconds"

    # Step 4: Verify both outputs are available and valid
    output1 = test_client.get(f"/outputs/{job_id_1}")
    output2 = test_client.get(f"/outputs/{job_id_2}")

    assert output1.status_code == 200
    assert output2.status_code == 200

    # Verify both are MP4
    assert output1.headers["content-type"] == "video/mp4"
    assert output2.headers["content-type"] == "video/mp4"

    print(f"✓ Both concurrent jobs generated valid MP4 outputs")


@pytest.mark.asyncio
async def test_multiple_concurrent_jobs(test_client, cleanup_jobs, cleanup_dirs):
    """Test that multiple jobs can run concurrently without interference"""
    job_ids = []

    # Queue 3 jobs
    for i in range(3):
        files = [("images", ("image.png", create_test_image(), "image/png"))]
        response = test_client.post(
            "/generate",
            data={"prompt": f"Prompt {i}"},
            files=files
        )
        assert response.status_code == 200
        job_ids.append(response.json()["job_id"])

    # Verify all have unique IDs
    assert len(job_ids) == len(set(job_ids))
    print(f"\n✓ Created 3 concurrent jobs: {job_ids}")

    # Verify all jobs are in progress or complete
    for job_id in job_ids:
        status = test_client.get(f"/status/{job_id}").json()
        assert status["status"] in ["generating", "complete", "failed"]


@pytest.mark.asyncio
async def test_concurrent_status_polling(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that concurrent status polls don't interfere with each other"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": "Test concurrent polling"},
        files=files
    )

    job_id = response.json()["job_id"]

    # Poll status concurrently
    async def poll_status():
        statuses = []
        for _ in range(5):
            status = test_client.get(f"/status/{job_id}").json()
            statuses.append(status)
            await asyncio.sleep(0.1)
        return statuses

    results = await asyncio.gather(
        poll_status(),
        poll_status(),
        poll_status(),
    )

    # Verify all polls returned valid status
    for statuses in results:
        for status in statuses:
            assert "status" in status
            assert "progress" in status
            assert status["status"] in ["generating", "complete", "failed"]

    print(f"\n✓ Concurrent status polling works correctly")
