## ADDED Requirements

### Requirement: POST /generate endpoint
The system SHALL provide a `/generate` endpoint that accepts image uploads and prompts, returns a job ID, and begins async generation.

#### Scenario: Submit generation request
- **WHEN** frontend POSTs multipart form data (images + prompt) to `/generate`
- **THEN** backend validates inputs, queues generation, returns `{job_id: string}`

#### Scenario: Invalid request rejected
- **WHEN** POST to `/generate` lacks images or prompt
- **THEN** backend returns 400 error with validation message

### Requirement: GET /status/{job_id} endpoint
The system SHALL provide a `/status/{job_id}` endpoint that returns current generation progress.

#### Scenario: Check generation progress
- **WHEN** frontend POLLs `/status/{job_id}` during generation
- **THEN** backend returns `{status: "generating" | "complete" | "failed", progress: 0-100, message: string}`

#### Scenario: Job not found
- **WHEN** frontend queries invalid job_id
- **THEN** backend returns 404 error

### Requirement: GET /outputs/{job_id} endpoint
The system SHALL provide a `/outputs/{job_id}` endpoint that returns the generated MP4 file.

#### Scenario: Download completed video
- **WHEN** generation completes and frontend GETs `/outputs/{job_id}`
- **THEN** backend serves MP4 file with correct content-type header

#### Scenario: Output not ready
- **WHEN** frontend requests `/outputs/{job_id}` before completion
- **THEN** backend returns 202 Accepted or error indicating incomplete generation

### Requirement: Error handling and logging
The system SHALL log generation errors and return meaningful error messages to frontend.

#### Scenario: Generation fails
- **WHEN** SDXL or AnimateDiff encounters error
- **THEN** backend logs stack trace, returns error response to `/status/{job_id}` with error message

#### Scenario: Out of memory
- **WHEN** VRAM is exhausted during generation
- **THEN** backend catches OOM error, frees memory, returns error response (no crash)

### Requirement: CORS headers for frontend
The system SHALL include CORS headers to allow frontend requests from localhost.

#### Scenario: Frontend calls backend
- **WHEN** Next.js frontend on localhost:3000 calls FastAPI backend on localhost:8000
- **THEN** backend includes `Access-Control-Allow-Origin` headers in responses
