from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageEnhance, ImageOps
import io
import os

app = FastAPI(title="Canva Image Toolkit API", version="0.1.0")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.get("/health")
def health():
    return {"status": "ok", "service": "canva-image-toolkit"}

async def read_image(file: UploadFile) -> Image.Image:
    data = await file.read()
    try:
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception as exc:
        raise HTTPException(400, "Arquivo de imagem inválido") from exc

def png_response(image: Image.Image):
    from fastapi.responses import Response
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return Response(buffer.getvalue(), media_type="image/png")

@app.post("/v1/image/adjust")
async def adjust(file: UploadFile = File(...), brightness: float = 1.0, contrast: float = 1.0, saturation: float = 1.0):
    image = await read_image(file)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Color(image).enhance(saturation)
    return png_response(image)

@app.post("/v1/image/flip")
async def flip(file: UploadFile = File(...), horizontal: bool = True):
    image = await read_image(file)
    return png_response(ImageOps.mirror(image) if horizontal else ImageOps.flip(image))

@app.post("/v1/image/upscale")
async def upscale(file: UploadFile = File(...), scale: int = 2):
    if scale not in (2, 4):
        raise HTTPException(400, "scale deve ser 2 ou 4")
    image = await read_image(file)
    result = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    return png_response(result)

@app.post("/v1/image/remove-background")
async def remove_background(file: UploadFile = File(...)):
    raise HTTPException(501, "Provider de remoção de fundo ainda não configurado")

@app.post("/v1/image/ocr")
async def ocr(file: UploadFile = File(...)):
    raise HTTPException(501, "Provider OCR ainda não configurado")
