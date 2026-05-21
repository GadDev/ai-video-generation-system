import torch
import logging
from typing import Optional
from diffusers import AnimateDiffPipeline, LCMScheduler, MotionAdapter
import os

logger = logging.getLogger(__name__)

BASE_MODEL = os.getenv("BASE_MODEL", "emilianJR/epiCRealism")
MOTION_ADAPTER = "wangfuyun/AnimateLCM"

def _get_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"

DEVICE = _get_device()
DTYPE = torch.float16 if DEVICE == "mps" else torch.float32


class ModelCache:
    def __init__(self):
        self.pipeline = None
        self.device = DEVICE
        logger.info(f"Using device: {self.device}")

    def load_animatediff_lcm(self) -> Optional[AnimateDiffPipeline]:
        if self.pipeline is not None:
            logger.info("AnimateDiff pipeline already cached")
            return self.pipeline

        try:
            logger.info(f"Loading AnimateLCM motion adapter from {MOTION_ADAPTER}...")
            adapter = MotionAdapter.from_pretrained(
                MOTION_ADAPTER,
                torch_dtype=DTYPE,
            )

            logger.info(f"Loading SD 1.5 base model from {BASE_MODEL}...")
            self.pipeline = AnimateDiffPipeline.from_pretrained(
                BASE_MODEL,
                motion_adapter=adapter,
                torch_dtype=DTYPE,
            )

            self.pipeline.scheduler = LCMScheduler.from_config(
                self.pipeline.scheduler.config,
                beta_schedule="linear",
            )

            logger.info("Loading AnimateLCM LoRA weights...")
            self.pipeline.load_lora_weights(
                MOTION_ADAPTER,
                weight_name="AnimateLCM_sd15_t2v_lora.safetensors",
                adapter_name="lcm-lora",
            )
            self.pipeline.set_adapters(["lcm-lora"], [0.8])

            self.pipeline.enable_vae_slicing()
            if DEVICE == "mps":
                self.pipeline.to("mps")
            else:
                self.pipeline.enable_model_cpu_offload()

            logger.info("✓ AnimateDiff + LCM pipeline loaded successfully")
            return self.pipeline

        except Exception as e:
            logger.error(f"Failed to load AnimateDiff pipeline: {str(e)}")
            raise

    def cleanup(self):
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None


model_cache = ModelCache()


async def warmup_models():
    logger.info(f"Using device: {DEVICE} (dtype: {'float16' if DTYPE == torch.float16 else 'float32'})")
    logger.info("Warming up models at startup...")
    try:
        model_cache.load_animatediff_lcm()
        logger.info("✓ Model warmup complete")
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
