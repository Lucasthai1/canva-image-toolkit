from io import BytesIO
import os
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
MAX_PIXELS = int(os.getenv("MAX_PIXELS", "25000000"))
MAX_OUTPUT_PIXELS = int(os.getenv("MAX_OUTPUT_PIXELS", "50000000"))
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "image/tiff", "image/bmp"}

app = FastAPI(title="Canva Image Toolkit API", version="0.2.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["*"], allow_credentials=True)

@app.get("/health")
def health():
    return {"status": "ok", "service": "canva-image-toolkit", "version": app.version}

async def read_image(file: UploadFile) -> Image.Image:
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Formato não suportado")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Imagem excede o limite de tamanho")
    try:
        image = Image.open(BytesIO(data))
        image.load()
        if image.width * image.height > MAX_PIXELS:
            raise HTTPException(413, "Imagem excede o limite de pixels")
        return ImageOps.exif_transpose(image).convert("RGBA")
    except UnidentifiedImageError as exc:
        raise HTTPException(400, "Arquivo de imagem inválido") from exc

def png_response(image: Image.Image) -> Response:
    if image.width * image.height > MAX_OUTPUT_PIXELS:
        raise HTTPException(413, "Resultado excede o limite de pixels")
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return Response(buffer.getvalue(), media_type="image/png", headers={"Cache-Control": "no-store"})

def bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

@app.post("/v1/image/adjust")
async def adjust(file: Annotated[UploadFile, File(...)], brightness: float = 1.0, contrast: float = 1.0, saturation: float = 1.0, sharpness: float = 1.0):
    image = await read_image(file)
    image = ImageEnhance.Brightness(image).enhance(bounded(brightness, 0, 3))
    image = ImageEnhance.Contrast(image).enhance(bounded(contrast, 0, 3))
    image = ImageEnhance.Color(image).enhance(bounded(saturation, 0, 3))
    image = ImageEnhance.Sharpness(image).enhance(bounded(sharpness, 0, 5))
    return png_response(image)

@app.post("/v1/image/flip")
async def flip(file: Annotated[UploadFile, File(...)], horizontal: bool = True):
    image = await read_image(file)
    return png_response(ImageOps.mirror(image) if horizontal else ImageOps.flip(image))

@app.post("/v1/image/rotate")
async def rotate(file: Annotated[UploadFile, File(...)], angle: float = 0):
    image = await read_image(file)
    return png_response(image.rotate(bounded(angle, -360, 360), expand=True, resample=Image.Resampling.BICUBIC))

@app.post("/v1/image/upscale")
async def upscale(file: Annotated[UploadFile, File(...)], scale: int = 2):
    if scale not in (2, 4):
        raise HTTPException(400, "scale deve ser 2 ou 4")
    image = await read_image(file)
    width, height = image.width * scale, image.height * scale
    if width * height > MAX_OUTPUT_PIXELS:
        raise HTTPException(413, "Upscale excede o limite de pixels")
    return png_response(image.resize((width, height), Image.Resampling.LANCZOS))

@app.post("/v1/image/remove-background")
async def remove_background(file: Annotated[UploadFile, File(...)]):
    raise HTTPException(501, "Configure um provider de remoção de fundo antes de usar este endpoint")

@app.post("/v1/image/ocr")
async def ocr(file: Annotated[UploadFile, File(...)]):
    raise HTTPException(501, "Configure um provider OCR antes de usar este endpoint")
