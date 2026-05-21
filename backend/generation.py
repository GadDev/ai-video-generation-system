import torch
import logging
import asyncio
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Optional
from models import model_cache
import os

logger = logging.getLogger(__name__)


def load_and_validate_image(image_path: str, size: Tuple[int, int] = (512, 512)) -> Optional[Image.Image]:
    """Load and validate image, resize if needed"""
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

        ref_image = load_and_validate_image(str(images[0]))
        return ref_image
    except Exception as e:
        logger.error(f"Error getting reference image: {str(e)}")
        return None


async def generate_sdxl_frame(
    prompt: str,
    reference_image: Optional[Image.Image] = None,
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
) -> Optional[Image.Image]:
    """Generate single frame using SDXL"""
    try:
        logger.info(f"Generating SDXL frame with prompt: {prompt[:50]}...")
        
        pipeline = model_cache.load_sdxl()
        if pipeline is None:
            logger.error("SDXL pipeline not available")
            return None

        with torch.inference_mode():
            if reference_image is not None:
                image = pipeline(
                    prompt=prompt,
                    image=reference_image,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=1024,
                    width=1024,
                ).images[0]
            else:
                image = pipeline(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=1024,
                    width=1024,
                ).images[0]

        logger.info("SDXL frame generated successfully")
        return image

    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            logger.error("GPU out of memory during SDXL generation")
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        else:
            logger.error(f"Runtime error in SDXL generation: {str(e)}")
    except Exception as e:
        logger.error(f"Error in SDXL generation: {str(e)}")
    
    return None


async def generate_animatediff_frames(
    base_image: Image.Image,
    prompt: str,
    num_frames: int = 16,
    num_inference_steps: int = 25,
) -> Optional[List[Image.Image]]:
    """Generate frame sequence using AnimateDiff"""
    try:
        logger.info(f"Generating AnimateDiff frames ({num_frames} frames)...")
        
        pipeline = model_cache.load_animatediff()
        if pipeline is None:
            logger.warning("AnimateDiff not available, using frame duplication fallback")
            frames = [base_image] * num_frames
            return frames

        with torch.inference_mode():
            frames = pipeline(
                prompt=prompt,
                image=base_image,
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
            ).frames[0]

        logger.info(f"AnimateDiff generated {len(frames)} frames")
        return frames

    except Exception as e:
        logger.warning(f"AnimateDiff generation failed, using fallback: {str(e)}")
        return [base_image] * num_frames


async def generate_video_frames(
    prompt: str,
    upload_dir: str,
    num_frames: int = 16,
    timeout_seconds: int = 300,
) -> Optional[List[Image.Image]]:
    """Main generation function with timeout"""
    try:
        start_time = asyncio.get_event_loop().time()

        reference_image = get_reference_image(upload_dir)
        if reference_image is None:
            logger.error("Failed to load reference image")
            return None

        sdxl_frame = await asyncio.wait_for(
            generate_sdxl_frame(prompt, reference_image),
            timeout=timeout_seconds * 0.5
        )
        if sdxl_frame is None:
            logger.error("SDXL generation failed")
            return None

        elapsed = asyncio.get_event_loop().time() - start_time
        remaining_timeout = timeout_seconds - elapsed
        
        if remaining_timeout <= 0:
            logger.error("Timeout exceeded during generation")
            return None

        frames = await asyncio.wait_for(
            generate_animatediff_frames(sdxl_frame, prompt, num_frames),
            timeout=remaining_timeout
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
