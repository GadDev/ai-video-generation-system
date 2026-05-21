## ADDED Requirements

### Requirement: Generate stylized image with SDXL
The system SHALL use Stable Diffusion XL (anime checkpoint) to generate a stylized image conditioned on the user's prompt and reference image.

#### Scenario: SDXL generates image from prompt
- **WHEN** backend receives valid prompt + reference image
- **THEN** SDXL generates a 1024×1024 anime-style image within 30–60 seconds

#### Scenario: SDXL uses anime checkpoint
- **WHEN** generation begins
- **THEN** backend loads Animagine XL or Juggernaut XL checkpoint (anime-tuned SDXL variant)

### Requirement: Create motion sequence with AnimateDiff
The system SHALL use AnimateDiff motion modules to generate 16–32 frames of temporal coherence from the SDXL-generated image.

#### Scenario: AnimateDiff creates frame sequence
- **WHEN** SDXL image generation completes
- **THEN** AnimateDiff generates 16–32 frames (~0.5–1.5 seconds at 24fps) of smooth motion

#### Scenario: AnimateDiff respects motion constraints
- **WHEN** AnimateDiff generates frames
- **THEN** system produces consistent, non-flickering output suitable for short anime clips

### Requirement: Optimize inference for Apple Silicon
The system SHALL use PyTorch MPS acceleration to offload inference to Apple Silicon GPU.

#### Scenario: MPS acceleration is enabled
- **WHEN** backend starts
- **THEN** system verifies `torch.backends.mps.is_available()` is True and configures device=mps

#### Scenario: Generation uses GPU acceleration
- **WHEN** SDXL + AnimateDiff inference runs
- **THEN** operations execute on Apple Silicon GPU, not CPU

### Requirement: Cache models in memory
The system SHALL load SDXL and AnimateDiff modules once at startup and reuse them across generation requests.

#### Scenario: Models loaded at startup
- **WHEN** backend initializes
- **THEN** SDXL and AnimateDiff models are loaded into memory (warmup phase)

#### Scenario: Subsequent requests use cached models
- **WHEN** `/generate` is called after first request
- **THEN** generation completes faster due to cached model weights

### Requirement: Handle generation timeout
The system SHALL timeout generation if it exceeds 5 minutes, returning error to frontend.

#### Scenario: Generation exceeds timeout
- **WHEN** SDXL + AnimateDiff exceed 5 minutes
- **THEN** backend cancels operation, frees memory, returns error response
