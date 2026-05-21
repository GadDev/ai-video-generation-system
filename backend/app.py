import os
import json
import uuid
import asyncio
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from models import model_cache, warmup_models
from generation import generate_video_frames
from video_export import frames_to_mp4, frames_to_gif, validate_video_file, cleanup_temp_files, validate_ffmpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Generation API")

# CORS configuration for localhost:3000 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

jobs = {}


class GenerationStatus(BaseModel):
    status: str
    progress: int
    message: str
    output_url: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Video Generation API")
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    validate_ffmpeg()
    await warmup_models()


@app.get("/")
async def root():
    return {"message": "AI Video Generation API"}


async def process_generation(job_id: str, prompt: str, upload_dir: str):
    """Background task: generate video frames and export to MP4"""
    try:
        jobs[job_id]["message"] = "Generating video frames..."
        jobs[job_id]["progress"] = 10

        frames = await generate_video_frames(prompt, upload_dir, num_frames=16, timeout_seconds=300)

        if frames is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "Frame generation failed"
            logger.error(f"Job {job_id}: Frame generation failed")
            return

        jobs[job_id]["progress"] = 60
        jobs[job_id]["message"] = "Exporting to MP4..."

        mp4_path = OUTPUT_DIR / f"{job_id}.mp4"
        success = frames_to_mp4(frames, str(mp4_path), fps=24)

        if not success:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "MP4 export failed"
            logger.error(f"Job {job_id}: MP4 export failed")
            return

        jobs[job_id]["progress"] = 90
        jobs[job_id]["message"] = "Validating video..."

        if not validate_video_file(str(mp4_path)):
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "Video validation failed"
            return

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["message"] = "Video generation complete"
        logger.info(f"Job {job_id}: Complete")

        shutil.rmtree(Path(upload_dir), ignore_errors=True)

    except asyncio.CancelledError:
        jobs[job_id]["status"] = "cancelled"
        logger.info(f"Job {job_id}: Cancelled")
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        logger.error(f"Job {job_id}: {str(e)}")


@app.post("/generate")
async def generate(prompt: str = Form(...), images: list[UploadFile] = File(...)):
    job_id = str(uuid.uuid4())

    try:
        if not prompt or len(prompt.strip()) == 0:
            return {"error": "Prompt cannot be empty"}, 400

        if len(prompt) > 500:
            return {"error": "Prompt exceeds 500 characters"}, 400

        if not images or len(images) == 0:
            return {"error": "At least one image is required"}, 400

        if len(images) > 5:
            return {"error": "Maximum 5 images allowed"}, 400

        job_upload_dir = UPLOAD_DIR / job_id
        job_upload_dir.mkdir(parents=True, exist_ok=True)

        for idx, image in enumerate(images):
            if image.filename:
                file_path = job_upload_dir / f"{idx}_{image.filename}"
                contents = await image.read()
                with open(file_path, "wb") as f:
                    f.write(contents)

        jobs[job_id] = {
            "status": "generating",
            "progress": 0,
            "message": "Initializing generation pipeline",
            "prompt": prompt,
            "upload_dir": str(job_upload_dir),
        }

        logger.info(f"Job {job_id} created with prompt: {prompt}")

        asyncio.create_task(process_generation(job_id, prompt, str(job_upload_dir)))

        return {"job_id": job_id}

    except Exception as e:
        logger.error(f"Error in /generate: {str(e)}")
        return {"error": str(e)}, 500


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": f"Job {job_id} not found"}, 404

    job = jobs[job_id]
    return GenerationStatus(
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        output_url=f"/outputs/{job_id}" if job["status"] == "complete" else None,
    )


@app.get("/outputs/{job_id}")
async def get_output(job_id: str):
    if job_id not in jobs:
        return {"error": f"Job {job_id} not found"}, 404

    job = jobs[job_id]
    if job["status"] != "complete":
        return {"error": "Generation not complete"}, 202

    video_path = OUTPUT_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        return {"error": "Video file not found"}, 404

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"generated_{job_id}.mp4",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
