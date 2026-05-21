## ADDED Requirements

### Requirement: Accept image uploads from user
The system SHALL accept 2–5 anime/person reference images (JPEG, PNG formats) via the frontend and store them temporarily for generation.

#### Scenario: User uploads valid images
- **WHEN** user selects 2–5 image files via file picker
- **THEN** frontend validates file format and size, uploads to backend, and displays thumbnails

#### Scenario: User uploads invalid file
- **WHEN** user attempts to upload non-image file or image >10MB
- **THEN** frontend shows error message and rejects upload

### Requirement: Parse uploaded images for reference
The system SHALL extract the first/main uploaded image as the reference frame for SDXL generation.

#### Scenario: Select primary reference image
- **WHEN** user uploads multiple images
- **THEN** system uses the first image as conditioning for SDXL generation

### Requirement: Store uploads temporarily
The system SHALL store uploaded images in a temporary directory and clean them up after generation completes.

#### Scenario: Cleanup after successful generation
- **WHEN** video export completes successfully
- **THEN** system deletes temporary image files from disk
