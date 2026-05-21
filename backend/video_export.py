import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)


def validate_ffmpeg() -> bool:
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            logger.info("✓ FFmpeg is available")
            return True
    except Exception as e:
        logger.error(f"FFmpeg not found: {str(e)}")
    return False


def frames_to_mp4(
    frames: List[Image.Image],
    output_path: str,
    fps: int = 24,
    codec: str = "libx264",
) -> bool:
    """Convert frame sequence to MP4 using FFmpeg"""
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_frames_dir = output_path.parent / f"temp_frames_{output_path.stem}"
        temp_frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving {len(frames)} frames to {temp_frames_dir}")
        for idx, frame in enumerate(frames):
            frame_path = temp_frames_dir / f"frame_{idx:04d}.png"
            frame.save(frame_path, "PNG")

        pattern = str(temp_frames_dir / "frame_%04d.png")
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-c:v", codec,
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            str(output_path),
        ]

        logger.info(f"Running FFmpeg: {' '.join(cmd[:5])} ... {cmd[-1]}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False

        logger.info(f"MP4 created: {output_path}")
        shutil.rmtree(temp_frames_dir, ignore_errors=True)
        
        return True

    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timeout")
        return False
    except Exception as e:
        logger.error(f"Error creating MP4: {str(e)}")
        return False



def validate_video_file(video_path: str) -> bool:
    """Validate video file with ffprobe"""
    try:
        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False

        if video_path.stat().st_size == 0:
            logger.error("Video file is empty")
            return False

        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type,codec_name,r_frame_rate,width,height",
            "-of", "default=noprint_wrappers=1",
            str(video_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            logger.error(f"ffprobe validation failed: {result.stderr}")
            return False

        logger.info(f"✓ Video file validated: {video_path.name}")
        logger.info(f"  Output:\n{result.stdout}")
        return True

    except subprocess.TimeoutExpired:
        logger.error("ffprobe timeout")
        return False
    except Exception as e:
        logger.error(f"Error validating video: {str(e)}")
        return False


def cleanup_temp_files(temp_dir: str) -> None:
    """Remove temporary files after generation"""
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Error cleaning up temp files: {str(e)}")
