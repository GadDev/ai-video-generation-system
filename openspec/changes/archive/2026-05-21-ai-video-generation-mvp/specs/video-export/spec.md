## ADDED Requirements

### Requirement: Assemble frames into MP4 video
The system SHALL use FFmpeg to convert the generated frame sequence into an MP4 video file at 24fps.

#### Scenario: FFmpeg creates MP4 from frames
- **WHEN** AnimateDiff frame generation completes
- **THEN** FFmpeg assembles frames into a .mp4 file with H.264 codec

#### Scenario: Video has correct framerate
- **WHEN** MP4 is created
- **THEN** video plays at 24fps (resulting in 0.67–1.33 second duration for 16–32 frames)

### Requirement: Support GIF export
The system SHALL optionally generate GIF output from frame sequences for web-friendly preview.

#### Scenario: GIF export requested
- **WHEN** generation completes and user requests GIF
- **THEN** system creates an animated .gif file from the frame sequence

### Requirement: Store output files
The system SHALL store generated videos in a persistent output directory and expose them via `/outputs/{job_id}` endpoint.

#### Scenario: MP4 output available for download
- **WHEN** video export completes
- **THEN** MP4 is stored on disk and accessible via API endpoint

#### Scenario: User downloads generated video
- **WHEN** user clicks download link in frontend
- **THEN** browser downloads MP4 file to local machine

### Requirement: Validate video output
The system SHALL verify that generated MP4 files are valid and non-empty before returning to user.

#### Scenario: Video file validation
- **WHEN** FFmpeg completes
- **THEN** system checks file size >0 and ffprobe confirms valid codec/framerate

#### Scenario: Corrupted export rejected
- **WHEN** FFmpeg produces invalid file
- **THEN** backend logs error and returns error response, does not expose broken file
