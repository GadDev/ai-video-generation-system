import torch
import logging
from pathlib import Path
from typing import Optional
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from PIL import Image
import os

logger = logging.getLogger(__name__)

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
MODEL_CHECKPOINT = os.getenv("MODEL_CHECKPOINT", "Animagine/Animagine-XL-3.0")


class ModelCache:
    def __init__(self):
        self.sdxl_pipeline = None
        self.animatediff_pipeline = None
        self.device = DEVICE
        logger.info(f"Using device: {self.device}")

    def load_sdxl(self):
        if self.sdxl_pipeline is not None:
            logger.info("SDXL model already cached")
            return self.sdxl_pipeline

        logger.info(f"Loading SDXL model from {MODEL_CHECKPOINT}")
        try:
            self.sdxl_pipeline = DiffusionPipeline.from_pretrained(
                MODEL_CHECKPOINT,
                torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
                variant="fp16" if self.device == "mps" else None,
            )
            self.sdxl_pipeline.to(self.device)
            self.sdxl_pipeline.enable_attention_slicing()
            logger.info("SDXL model loaded successfully")
            return self.sdxl_pipeline
        except Exception as e:
            logger.error(f"Failed to load SDXL model: {str(e)}")
            raise

    def load_animatediff(self):
        if self.animatediff_pipeline is not None:
            logger.info("AnimateDiff model already cached")
            return self.animatediff_pipeline

        logger.info("Loading AnimateDiff motion module")
        try:
            from animatediff import get_context_scheduler
            from animatediff.pipelines import TextToVideoPipeline

            self.animatediff_pipeline = TextToVideoPipeline.from_pretrained(
                MODEL_CHECKPOINT,
                torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
            )
            self.animatediff_pipeline.to(self.device)
            logger.info("AnimateDiff model loaded successfully")
            return self.animatediff_pipeline
        except Exception as e:
            logger.warning(f"AnimateDiff loading warning: {str(e)}")
            logger.info("Falling back to basic frame generation")
            return None

    def verify_mps(self):
        if torch.backends.mps.is_available():
            logger.info("✓ PyTorch MPS acceleration available")
            logger.info(f"  MPS device: {torch.mps.get_device_properties(0)}")
            return True
        else:
            logger.warning("✗ PyTorch MPS not available, using CPU")
            return False

    def cleanup(self):
        if self.sdxl_pipeline is not None:
            del self.sdxl_pipeline
            self.sdxl_pipeline = None
        if self.animatediff_pipeline is not None:
            del self.animatediff_pipeline
            self.animatediff_pipeline = None
        torch.cuda.empty_cache() if torch.cuda.is_available() else None


model_cache = ModelCache()


async def warmup_models():
    logger.info("Warming up models at startup...")
    model_cache.verify_mps()
    try:
        model_cache.load_sdxl()
        logger.info("✓ Model warmup complete")
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
