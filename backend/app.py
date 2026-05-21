import os
import uuid
import asyncio
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from models import warmup_models
from generation import generate_video_frames
from video_export import frames_to_mp4, validate_video_file, validate_ffmpeg

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
job_tasks = {}
JOB_TTL_SECONDS = 3600  # Remove completed/failed jobs after 1 hour


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
    asyncio.create_task(cleanup_old_jobs())


async def cleanup_old_jobs():
    """Periodically remove completed/failed jobs older than JOB_TTL_SECONDS"""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        now = asyncio.get_event_loop().time()
        to_delete = [
            job_id for job_id, job in jobs.items()
            if job["status"] in ("complete", "failed", "cancelled")
            and now - job.get("created_at", now) > JOB_TTL_SECONDS
        ]
        for job_id in to_delete:
            jobs.pop(job_id, None)
            job_tasks.pop(job_id, None)
            logger.info(f"Cleaned up expired job: {job_id}")


@app.get("/")
async def root():
    return {"message": "AI Video Generation API"}


async def process_generation(job_id: str, prompt: str, upload_dir: str):
    """Background task: generate video frames and export to MP4"""
    try:
        jobs[job_id]["message"] = "Initializing generation pipeline..."
        jobs[job_id]["progress"] = 1

        start_time = asyncio.get_event_loop().time()

        # Phase 1: AnimateDiff + LCM frame generation (2-65%)
        jobs[job_id]["progress"] = 2
        jobs[job_id]["message"] = "🎬 Generating animated frames with AnimateLCM (6 steps)..."

        # Background task to update progress during generation
        async def update_progress_during_generation():
            """Update progress every 2 seconds — AnimateLCM takes ~3-5 min on CPU"""
            while True:
                try:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    # AnimateLCM 6 steps on CPU ~180-300s (3-5 min), progress 2-65%
                    progress = min(63, int(2 + (elapsed / 300) * 63))
                    jobs[job_id]["progress"] = progress
                    jobs[job_id]["message"] = f"🎬 Generating animated frames... {progress}%"
                    await asyncio.sleep(2)
                except Exception:
                    await asyncio.sleep(2)

        progress_task = asyncio.create_task(update_progress_during_generation())

        try:
            frames = await generate_video_frames(prompt, upload_dir, num_frames=16, timeout_seconds=600)
        finally:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        if frames is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "❌ Frame generation failed"
            logger.error(f"Job {job_id}: Frame generation failed")
            return

        generation_time = asyncio.get_event_loop().time() - start_time
        logger.info(f"Job {job_id}: Frame generation completed in {generation_time:.1f}s")

        jobs[job_id]["progress"] = 65
        jobs[job_id]["message"] = f"🎬 {len(frames)} animated frames ready"

        # Phase 2: MP4 export (65-85%)
        jobs[job_id]["progress"] = 70
        jobs[job_id]["message"] = "📹 Exporting to MP4..."

        mp4_path = OUTPUT_DIR / f"{job_id}.mp4"
        success = frames_to_mp4(frames, str(mp4_path), fps=8)

        if not success:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "❌ MP4 export failed"
            logger.error(f"Job {job_id}: MP4 export failed")
            return

        jobs[job_id]["progress"] = 80
        jobs[job_id]["message"] = "📹 MP4 encoded successfully"

        # Phase 3: Validation (80-100%)
        jobs[job_id]["progress"] = 85
        jobs[job_id]["message"] = "✅ Validating video..."

        if not validate_video_file(str(mp4_path)):
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["message"] = "❌ Video validation failed"
            return

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["message"] = "✅ Video ready to download!"
        logger.info(f"Job {job_id}: Complete")

        shutil.rmtree(Path(upload_dir), ignore_errors=True)

    except asyncio.CancelledError:
        if jobs[job_id]["status"] == "generating":
            jobs[job_id]["status"] = "cancelled"
            jobs[job_id]["message"] = "Generation cancelled"
        logger.info(f"Job {job_id}: Cancelled")
        # Cleanup temp files on cancellation
        shutil.rmtree(Path(upload_dir), ignore_errors=True)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        logger.error(f"Job {job_id}: {str(e)}")


@app.post("/generate")
async def generate(prompt: str = Form(...), images: list[UploadFile] = File(default=[])):
    job_id = str(uuid.uuid4())

    try:
        if not prompt or len(prompt.strip()) == 0:
            return {"error": "Prompt cannot be empty"}, 400

        if len(prompt) > 500:
            return {"error": "Prompt exceeds 500 characters"}, 400

        if images and len(images) > 5:
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
            "created_at": asyncio.get_event_loop().time(),
        }

        logger.info(f"Job {job_id} created with prompt: {prompt}")

        task = asyncio.create_task(process_generation(job_id, prompt, str(job_upload_dir)))
        job_tasks[job_id] = task

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


@app.delete("/generate/{job_id}")
async def cancel_generation(job_id: str):
    """Cancel an in-progress generation job"""
    if job_id not in jobs:
        return {"error": f"Job {job_id} not found"}, 404

    job = jobs[job_id]

    # Can only cancel if still generating
    if job["status"] != "generating":
        return {"error": f"Cannot cancel job with status: {job['status']}"}, 400

    # Cancel the async task
    if job_id in job_tasks:
        task = job_tasks[job_id]
        task.cancel()
        logger.info(f"Job {job_id}: Cancellation requested")

    jobs[job_id]["status"] = "cancelled"
    jobs[job_id]["message"] = "Generation cancelled by user"
    jobs[job_id]["progress"] = 0

    return {"job_id": job_id, "status": "cancelled"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
