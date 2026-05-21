## ADDED Requirements

### Requirement: Image upload component
The system SHALL provide a drag-and-drop file input that accepts 2–5 anime/person images (JPEG, PNG).

#### Scenario: User drags images onto upload area
- **WHEN** user drags image files onto the upload zone
- **THEN** frontend accepts drop, displays file names and thumbnails

#### Scenario: User clicks to select images
- **WHEN** user clicks upload button and selects files from file picker
- **THEN** frontend displays selected images with ability to remove/reorder

### Requirement: Prompt input field
The system SHALL provide a text input that accepts generation prompts up to 500 characters.

#### Scenario: User enters prompt
- **WHEN** user types prompt in text field
- **THEN** frontend shows character count and enables submit if images + prompt are valid

### Requirement: Generate button
The system SHALL provide a button that submits the generation request and begins polling status.

#### Scenario: User clicks Generate
- **WHEN** user clicks "Generate" with valid images + prompt
- **THEN** frontend sends `/generate` request and transitions to progress view

#### Scenario: Generate button disabled during generation
- **WHEN** generation is in progress
- **THEN** "Generate" button is disabled to prevent double-submission

### Requirement: Progress indicator
The system SHALL display real-time progress (estimated time remaining, current step) during generation.

#### Scenario: Poll status and show progress
- **WHEN** generation is running
- **THEN** frontend polls `/status/{job_id}` every 2 seconds and displays progress bar + estimated ETA

### Requirement: Video preview
The system SHALL display the generated MP4 video in an HTML5 video player once generation completes.

#### Scenario: Video plays after completion
- **WHEN** frontend receives status="complete"
- **THEN** video player loads from `/outputs/{job_id}` and displays generated clip

#### Scenario: User downloads video
- **WHEN** video is displayed
- **THEN** user can click download button to save MP4 to local machine

### Requirement: Error handling
The system SHALL display user-friendly error messages if generation fails.

#### Scenario: Generation fails
- **WHEN** backend returns error in `/status/{job_id}`
- **THEN** frontend displays error message and allows user to retry with new inputs

### Requirement: Responsive layout
The system SHALL be functional on desktop browsers (Chrome, Safari, Firefox) at standard resolutions.

#### Scenario: UI renders on desktop
- **WHEN** frontend loads on desktop browser
- **THEN** layout is readable, inputs accessible, video player properly sized
