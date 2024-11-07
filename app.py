# app.py
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import whisper
import tempfile
import os
from enum import Enum
import shutil
from typing import Optional
import uvicorn

class ModelSize(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"

app = FastAPI(
    title="Audio Transcription API",
    description="A FastAPI service for transcribing audio files using OpenAI's Whisper model"
)

# Mount templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables
model = None
current_model_size = None
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'wma', 'aac'}

def is_valid_audio_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.on_event("startup")
async def startup_event():
    global model, current_model_size
    model = whisper.load_model("base")
    current_model_size = "base"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile, background_tasks: BackgroundTasks):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not is_valid_audio_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        background_tasks.add_task(os.unlink, tmp_path)
        result = model.transcribe(tmp_path)
        
        return {
            "text": result["text"],
            "language": result["language"],
            "duration": result.get("duration", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)