import torch
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
from typing import List, Optional, Tuple
from models import model_cache, DEVICE
import os

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1)


def load_and_validate_image(image_path: str, size: Tuple[int, int] = (512, 512)) -> Optional[Image.Image]:
    """Load and resize a reference image"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None
        img = Image.open(image_path).convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        logger.info(f"Loaded image: {image_path} -> {size}")
        return img
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {str(e)}")
        return None


def get_reference_image(upload_dir: str) -> Optional[Image.Image]:
    """Get first reference image from upload directory"""
    try:
        upload_path = Path(upload_dir)
        images = sorted(upload_path.glob("*.*"))
        if not images:
            logger.error(f"No images found in {upload_dir}")
            return None
        return load_and_validate_image(str(images[0]))
    except Exception as e:
        logger.error(f"Error getting reference image: {str(e)}")
        return None


def generate_animated_frames(
    prompt: str,
    num_frames: int = 16,
    num_inference_steps: int = 6,
    guidance_scale: float = 2.0,
) -> Optional[List[Image.Image]]:
    """Generate animated frames using AnimateDiff + AnimateLCM (synchronous, runs in thread pool)"""
    try:
        logger.info(f"Generating {num_frames} animated frames: {prompt[:60]}... ({num_inference_steps} steps)")

        pipeline = model_cache.load_animatediff_lcm()
        if pipeline is None:
            logger.error("AnimateDiff pipeline not available")
            return None

        with torch.inference_mode():
            output = pipeline(
                prompt=prompt,
                negative_prompt="bad quality, worse quality, low resolution, blurry, distorted",
                num_frames=num_frames,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                generator=torch.Generator(DEVICE).manual_seed(42),
            )

        frames = output.frames[0]
        logger.info(f"✓ Generated {len(frames)} animated frames")
        return frames

    except RuntimeError as e:
        logger.error(f"Runtime error in AnimateDiff generation: {str(e)}")
    except Exception as e:
        logger.error(f"Error in AnimateDiff generation: {str(e)}")

    return None


async def generate_video_frames(
    prompt: str,
    upload_dir: str,
    num_frames: int = 16,
    timeout_seconds: int = 600,
) -> Optional[List[Image.Image]]:
    """Generate animated frames — runs inference in thread pool to keep event loop free"""
    try:
        start_time = asyncio.get_event_loop().time()

        # Log reference image if provided (not used in generation yet, reserved for future img2video)
        reference_image = get_reference_image(upload_dir)
        if reference_image is not None:
            logger.info("Reference image found (reserved for future img2video support)")
        else:
            logger.info("No reference image — generating from prompt only")

        loop = asyncio.get_event_loop()
        frames = await asyncio.wait_for(
            loop.run_in_executor(
                _executor,
                generate_animated_frames,
                prompt,
                num_frames,
            ),
            timeout=timeout_seconds,
        )

        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"Video frame generation completed in {elapsed:.1f}s")
        return frames

    except asyncio.TimeoutError:
        logger.error("Generation timeout exceeded")
        return None
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
        return None
