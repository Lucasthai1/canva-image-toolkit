from __future__ import annotations

from collections.abc import Iterable
from io import BytesIO

import cv2
import numpy as np
from config import Settings
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "image/tiff", "image/bmp"}
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP", "TIFF", "BMP"}
FORMAT_MIME = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
    "TIFF": "image/tiff",
    "BMP": "image/bmp",
}


async def read_upload(
    file: UploadFile, settings: Settings
) -> tuple[bytes, Image.Image]:
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Formato não suportado")
    data = await file.read(settings.max_upload_bytes + 1)
    if not data:
        raise HTTPException(400, "Arquivo vazio")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, "Imagem excede o limite de tamanho")
    try:
        with Image.open(BytesIO(data)) as source:
            detected_type = FORMAT_MIME.get(source.format or "")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(400, "Arquivo de imagem inválido") from exc
    if file.content_type and detected_type and file.content_type != detected_type:
        raise HTTPException(415, "MIME declarado não corresponde ao conteúdo")
    image = decode_image(data, settings)
    return data, image


def decode_image(data: bytes, settings: Settings) -> Image.Image:
    try:
        with Image.open(BytesIO(data)) as source:
            source.verify()
        with Image.open(BytesIO(data)) as source:
            source.load()
            if source.format not in ALLOWED_FORMATS:
                raise HTTPException(415, "Conteúdo da imagem não suportado")
            if source.width * source.height > settings.max_pixels:
                raise HTTPException(413, "Imagem excede o limite de pixels")
            return ImageOps.exif_transpose(source).convert("RGBA")
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(400, "Arquivo de imagem inválido") from exc


def encode_png(image: Image.Image, settings: Settings) -> bytes:
    if image.width * image.height > settings.max_output_pixels:
        raise HTTPException(413, "Resultado excede o limite de pixels")
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def adjust_image(
    image: Image.Image,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0,
) -> Image.Image:
    image = ImageEnhance.Brightness(image).enhance(bounded(brightness, 0, 3))
    image = ImageEnhance.Contrast(image).enhance(bounded(contrast, 0, 3))
    image = ImageEnhance.Color(image).enhance(bounded(saturation, 0, 3))
    return ImageEnhance.Sharpness(image).enhance(bounded(sharpness, 0, 5))


def upscale_lanczos(image: Image.Image, scale: int, settings: Settings) -> Image.Image:
    if scale not in (2, 4):
        raise HTTPException(400, "scale deve ser 2 ou 4")
    width, height = image.width * scale, image.height * scale
    if width * height > settings.max_output_pixels:
        raise HTTPException(413, "Upscale excede o limite de pixels")
    return image.resize((width, height), Image.Resampling.LANCZOS)


def perspective_image(
    image: Image.Image,
    points: Iterable[Iterable[float]],
    output_size: tuple[int, int],
    settings: Settings,
) -> Image.Image:
    source = np.asarray(list(points), dtype=np.float32)
    if source.shape != (4, 2) or not np.isfinite(source).all():
        raise HTTPException(400, "points deve conter quatro pontos finitos [x, y]")
    width, height = output_size
    if width <= 0 or height <= 0 or width * height > settings.max_output_pixels:
        raise HTTPException(
            413 if width * height > settings.max_output_pixels else 400,
            "Dimensões de saída inválidas",
        )
    destination = np.float32(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
    )
    matrix = cv2.getPerspectiveTransform(source, destination)
    array = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGRA)
    warped = cv2.warpPerspective(
        array, matrix, (width, height), borderMode=cv2.BORDER_TRANSPARENT
    )
    return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA))
