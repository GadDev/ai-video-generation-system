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
    num_inference_steps: int = 40,
    guidance_scale: float = 7.5,
) -> Optional[Image.Image]:
    """Generate single frame using SDXL Base + Refiner pipeline

    Args:
        prompt: Text prompt for generation
        reference_image: Optional reference image for style conditioning
        num_inference_steps: Total steps (32 base + 8 refiner = 40 recommended)
        guidance_scale: How much to follow the prompt (default 7.5)
    """
    try:
        base_steps = int(num_inference_steps * 0.8)
        refiner_steps = num_inference_steps - base_steps
        logger.info(f"Generating SDXL frame: {prompt[:50]}... ({base_steps} base + {refiner_steps} refiner steps)")

        base_pipeline = model_cache.load_sdxl()
        if base_pipeline is None:
            logger.error("SDXL base pipeline not available")
            return None

        # Phase 1: Base model generation
        with torch.inference_mode():
            if reference_image is not None:
                image = base_pipeline(
                    prompt=prompt,
                    image=reference_image,
                    num_inference_steps=base_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512,
                    output_type="latent",
                ).images[0]
            else:
                image = base_pipeline(
                    prompt=prompt,
                    num_inference_steps=base_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512,
                    output_type="latent",
                ).images[0]

        logger.info(f"Base model generated latent, refining with {refiner_steps} steps...")

        # Phase 2: Refiner model for final denoising
        refiner_pipeline = model_cache.load_sdxl_refiner()
        if refiner_pipeline is not None:
            with torch.inference_mode():
                image = refiner_pipeline(
                    prompt=prompt,
                    image=image,
                    num_inference_steps=refiner_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512,
                ).images[0]
            logger.info("SDXL refiner completed, high-quality frame generated")
        else:
            logger.warning("Refiner not available, using base model output only")
            with torch.inference_mode():
                image = base_pipeline(
                    prompt=prompt,
                    num_inference_steps=base_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512,
                ).images[0]

        return image

    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            logger.error("Out of memory during SDXL generation")
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
    """Generate frame sequence using AnimateDiff (or frame duplication if unavailable)"""
    try:
        logger.info(f"Generating {num_frames} frames...")

        pipeline = model_cache.load_animatediff()
        if pipeline is None:
            # AnimateDiff not available - use simple frame duplication
            logger.info("AnimateDiff unavailable, using frame duplication")
            frames = [base_image] * num_frames
            logger.info(f"✓ Created {len(frames)} frames via duplication")
            return frames

        # Try AnimateDiff generation
        with torch.inference_mode():
            frames = pipeline(
                prompt=prompt,
                image=base_image,
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
            ).frames[0]

        logger.info(f"✓ AnimateDiff generated {len(frames)} frames")
        return frames

    except Exception as e:
        logger.error(f"Frame generation error: {str(e)}", exc_info=True)
        # Fallback to frame duplication
        logger.info(f"Falling back to frame duplication ({num_frames} frames)")
        fallback_frames = [base_image] * num_frames
        logger.info(f"✓ Created {len(fallback_frames)} fallback frames")
        return fallback_frames


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
            logger.info("No reference image found, generating from prompt alone")

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
