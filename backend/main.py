from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
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
async def generate_pdf(body: GenerateRequest):
    try:
        pdf_path = await download_all_pages(
            start_url=body.start_url,
            base_url=body.base_url,
            next_selector=body.next_selector,
            output_filename=body.output_filename,
            dark_mode=body.dark_mode,
        )
        filename = os.path.basename(pdf_path)
        return JSONResponse(
            {
                "message": "PDF generated successfully",
                "filename": filename,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
