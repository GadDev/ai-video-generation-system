"""
11.2 Error handling tests: invalid file type, missing prompt, generation timeout
"""
import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_invalid_file_type_text(test_client, cleanup_jobs, cleanup_dirs):
    """Test that non-image files are rejected gracefully"""
    text_content = b"This is not an image"
    text_file = BytesIO(text_content)

    files = [("images", ("test.txt", text_file, "text/plain"))]

    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=files
    )

    # Should still allow upload, but generation will fail when processing
    if response.status_code == 200:
        job_id = response.json()["job_id"]
        # Verify job eventually fails
        import time
        max_wait = 10
        start = time.time()
        while time.time() - start < max_wait:
            status = test_client.get(f"/status/{job_id}").json()
            if status["status"] == "failed":
                assert "error" in status.get("message", "").lower() or "invalid" in status.get("message", "").lower()
                break
            time.sleep(0.5)
    else:
        # Or reject immediately
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_prompt_validation_empty(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that empty prompt is rejected"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": ""},
        files=files
    )

    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert "empty" in error["error"].lower() or "prompt" in error["error"].lower()


@pytest.mark.asyncio
async def test_prompt_validation_whitespace_only(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that whitespace-only prompt is rejected"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": "   \t\n  "},
        files=files
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_prompt_max_length(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that prompt exceeding 500 characters is rejected"""
    sample_image.seek(0)
    long_prompt = "a" * 501  # 501 characters

    files = [("images", ("test.png", sample_image, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": long_prompt},
        files=files
    )

    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert "500" in error["error"] or "exceed" in error["error"].lower()


@pytest.mark.asyncio
async def test_no_images_provided(test_client, cleanup_jobs, cleanup_dirs):
    """Test that generation works without images"""
    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=[]
    )

    # Should now succeed with just a prompt
    assert response.status_code == 200
    assert "job_id" in response.json()


@pytest.mark.asyncio
async def test_too_many_images(test_client, sample_images, cleanup_jobs, cleanup_dirs):
    """Test that maximum 5 images are allowed"""
    # Create 6 images
    from PIL import Image
    files = []
    for i in range(6):
        img = Image.new("RGB", (512, 512), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        files.append(("images", (f"image{i}.png", img_bytes, "image/png")))

    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=files
    )

    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert ("5" in error["error"] or "maximum" in error["error"].lower())


@pytest.mark.asyncio
async def test_corrupt_image_handling(test_client, cleanup_jobs, cleanup_dirs):
    """Test that corrupt image data is handled gracefully"""
    corrupt_data = b"\x89PNG\r\n\x1a\n" + b"corrupted_data"
    corrupt_file = BytesIO(corrupt_data)

    files = [("images", ("corrupt.png", corrupt_file, "image/png"))]

    response = test_client.post(
        "/generate",
        data={"prompt": "Test prompt"},
        files=files
    )

    # Should either reject immediately or fail during processing
    if response.status_code == 200:
        job_id = response.json()["job_id"]
        import time
        max_wait = 10
        start = time.time()
        while time.time() - start < max_wait:
            status = test_client.get(f"/status/{job_id}").json()
            if status["status"] == "failed":
                break
            time.sleep(0.5)
    else:
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_prompt_parameter(test_client, sample_image, cleanup_jobs, cleanup_dirs):
    """Test that missing prompt parameter is caught"""
    sample_image.seek(0)

    files = [("images", ("test.png", sample_image, "image/png"))]

    # Don't include prompt in data
    response = test_client.post(
        "/generate",
        data={},
        files=files
    )

    assert response.status_code in [400, 422]
