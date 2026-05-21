## ADDED Requirements

### Requirement: Accept text prompts for generation
The system SHALL accept freeform text prompts (e.g., "cyberpunk rooftop at sunset, cinematic camera movement") from the user for video generation.

#### Scenario: User enters valid prompt
- **WHEN** user types a prompt and clicks "Generate"
- **THEN** backend receives prompt, validates non-empty, and begins generation

#### Scenario: User submits empty prompt
- **WHEN** user clicks "Generate" with empty prompt field
- **THEN** frontend shows error message and prevents submission

### Requirement: Prompt length validation
The system SHALL enforce a maximum prompt length of 500 characters to prevent excessively long SDXL conditioning.

#### Scenario: User enters prompt over limit
- **WHEN** user types prompt exceeding 500 characters
- **THEN** frontend disables submit button and shows character count warning

### Requirement: Pass prompt to generation backend
The system SHALL send the user's prompt to the backend generation API for SDXL image synthesis.

#### Scenario: Prompt reaches generation pipeline
- **WHEN** user submits prompt + images
- **THEN** backend receives prompt in `/generate` request and uses it for SDXL conditioning
