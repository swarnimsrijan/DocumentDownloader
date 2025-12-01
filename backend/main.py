from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from uuid import uuid4
from job_manager import job_status
from downloader import download_all_pages
from fastapi import BackgroundTasks
import os

from downloader import download_all_pages


class GenerateRequest(BaseModel):
    start_url: str
    base_url: str
    next_selector: str
    output_filename: str = "merged.pdf"
    dark_mode: bool = False


app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate")
async def generate_pdf(body: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    job_status[job_id] = {"status": "starting", "done": False, "message": "Initializing"}

    background_tasks.add_task(
        download_all_pages,
        job_id,
        body.start_url,
        body.base_url,
        body.next_selector,
        body.output_filename,
        body.dark_mode,
    )

    return {"job_id": job_id}


@app.get("/download")
async def download_pdf(filename: str = Query(..., description="Name of the generated PDF")):
    file_path = os.path.join("output", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename,
    )

@app.get("/progress/{job_id}")
async def progress(job_id: str):
    return job_status.get(job_id, {"status": "unknown"})

