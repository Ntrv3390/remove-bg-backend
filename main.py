from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from rembg import remove
from PIL import Image
import uuid, os
from threading import Timer

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def delete_after(filepath, seconds=600):
    def delete():
        if os.path.exists(filepath):
            os.remove(filepath)
    Timer(seconds, delete).start()

@app.post("/remove-bg/")
async def remove_bg(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4()) + ".png"
    input_path = os.path.join(UPLOAD_DIR, file_id)
    output_path = os.path.join(OUTPUT_DIR, file_id)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)

    delete_after(input_path)
    delete_after(output_path)

    return {"url": f"/download/{file_id}"}

@app.get("/download/{filename}")
async def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png", filename=filename)
    return {"error": "File not found"}

