# Integration Tests for AI Video Generation System

This directory contains comprehensive integration tests for the AI video generation system, covering all aspects of the API and generation pipeline.

## Test Files

### test_e2e.py
**End-to-end workflow tests (Task 11.1)**

Tests the complete user workflow:
- Image upload validation
- Prompt validation
- Job creation and status tracking
- Video generation completion
- MP4 download and validation

Key tests:
- `test_e2e_full_workflow`: Complete upload → generate → download flow
- `test_generate_endpoint_invalid_prompt`: Empty prompt rejection
- `test_generate_endpoint_no_images`: Image requirement validation
- `test_status_nonexistent_job`: 404 on missing job
- `test_output_not_ready`: Status codes during generation

### test_error_handling.py
**Error handling tests (Task 11.2)**

Tests error conditions and edge cases:
- Invalid file types (text, corrupted images)
- Empty/whitespace-only prompts
- Prompt length validation (max 500 chars)
- Image count validation (1-5 images)
- Missing parameters

Key tests:
- `test_invalid_file_type_text`: Non-image files
- `test_prompt_validation_*`: Prompt validation
- `test_too_many_images`: Image count limits
- `test_corrupt_image_handling`: Corrupted image data

### test_mps_acceleration.py
**GPU acceleration tests (Task 11.3)**

Tests Apple Silicon MPS acceleration:
- MPS availability detection
- Device allocation verification
- Memory usage monitoring
- Tensor operations on correct device

Key tests:
- `test_mps_availability`: Check if MPS is available
- `test_device_allocation`: Verify device selection
- `test_model_loading_memory`: Memory usage during load
- `test_mps_tensor_operations`: Tensor ops on MPS

### test_model_caching.py
**Model caching tests (Task 11.4)**

Tests that models are properly cached and reused:
- First load vs. cached load timing
- Cache state persistence
- Concurrent cache access
- Cache cleanup

Key tests:
- `test_model_cache_hits`: Second load faster than first
- `test_model_cache_state`: Object identity across loads
- `test_concurrent_cache_access`: Thread-safe caching
- `test_cleanup_clears_cache`: Proper cleanup

### test_concurrent_requests.py
**Concurrent request tests (Task 11.5)**

Tests that multiple generations can run concurrently:
- Starting multiple jobs simultaneously
- Status polling without interference
- Both jobs completing successfully
- Separate outputs for each job

Key tests:
- `test_concurrent_generation_requests`: Two jobs running in parallel
- `test_multiple_concurrent_jobs`: Three concurrent jobs
- `test_concurrent_status_polling`: Parallel status checks

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run specific test file
```bash
pytest tests/test_e2e.py
```

### Run specific test
```bash
pytest tests/test_e2e.py::test_e2e_full_workflow
```

### Run with verbose output
```bash
pytest -v
```

### Run excluding slow tests
```bash
pytest -m "not slow"
```

### Run with detailed logging
```bash
pytest -v -s
```

## Test Configuration

Tests are configured via `pytest.ini`:
- Async test mode enabled via `asyncio_mode = auto`
- 600-second timeout for each test
- Log output to console at INFO level
- Test discovery from `test_*.py` files

## Test Fixtures

Common fixtures defined in `conftest.py`:
- `test_client`: FastAPI TestClient instance
- `sample_image`: Single test image (PIL Image in BytesIO)
- `sample_images`: Multiple test images
- `cleanup_jobs`: Clear jobs dict before/after test
- `cleanup_dirs`: Clean upload/output dirs before/after test
- `mps_available`: Check if MPS acceleration is available

## Hardware Requirements

- **CPU**: Tests run on any system (CPU fallback if no MPS)
- **GPU**: MPS tests require Apple Silicon (M1/M2/M3)
- **Memory**: Model loading tests use 100MB+ for safety checks
- **Storage**: Output directory needs ~100MB+ for generated videos

## Expected Behavior

### Local Development (MPS Available)
- MPS tests will verify GPU acceleration
- Model caching tests show <100ms for cached loads
- Memory usage monitoring shows GPU memory allocation
- E2E tests generate actual videos (slow, may take 2-5 min)

### CI/Local Testing (No GPU)
- MPS tests will skip gracefully
- Error handling tests verify validation logic
- Concurrent request tests verify job queuing
- Most tests complete in seconds (except full generation)

## Debugging Failed Tests

1. **Model download issues**: Check HF_HOME and internet connection
2. **File permissions**: Ensure uploads/ and outputs/ are writable
3. **Memory issues**: Monitor with `top` or `Activity Monitor`
4. **Timeout errors**: Increase timeout in pytest.ini if needed
5. **MPS errors**: Check `torch.backends.mps.is_available()`

## CI/CD Integration

For automated testing, consider:
1. Skip MPS tests on non-Apple systems
2. Use mock models for faster tests
3. Set timeouts based on CI environment
4. Preserve logs for debugging failures
