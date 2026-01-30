from fastapi import FastAPI, Request, BackgroundTasks, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from processing import download_video, process_video

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Mount processed directory to serve downloads
app.mount("/downloads", StaticFiles(directory="processed"), name="downloads")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/process")
async def process_url(url: str = Form(...)):
    try:
        # 1. Download
        raw_file_path = download_video(url)
        
        # 2. Process (Blocking for simplicity in this MVP, or could be background task with polling)
        # For a better UX with long loading times, we'd use websockets or polling. 
        # But for "simple script", we'll just await it.
        generated_files = process_video(raw_file_path)
        
        # Clean up raw download
        if os.path.exists(raw_file_path):
            os.remove(raw_file_path)

        return JSONResponse({
             "status": "success", 
             "videos": generated_files,
             "message": "Videos generated successfully!"
        })

    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
