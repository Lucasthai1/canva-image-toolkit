from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps


def load_image(path: str | Path) -> Image.Image:
    with Image.open(path) as source:
        source.load()
        return ImageOps.exif_transpose(source).convert("RGBA")


def save_image(image: Image.Image, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    suffix = target.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("output deve terminar em .png, .jpg, .jpeg ou .webp")
    if suffix in {".jpg", ".jpeg"}:
        image.convert("RGB").save(target, format="JPEG", quality=95, optimize=True)
    elif suffix == ".webp":
        image.save(target, format="WEBP", quality=95, method=6)
    else:
        image.save(target, format="PNG", optimize=True)


def adjust(image: Image.Image, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0) -> Image.Image:
    image = ImageEnhance.Brightness(image).enhance(max(0, min(3, brightness)))
    image = ImageEnhance.Contrast(image).enhance(max(0, min(3, contrast)))
    image = ImageEnhance.Color(image).enhance(max(0, min(3, saturation)))
    return ImageEnhance.Sharpness(image).enhance(max(0, min(5, sharpness)))


def upscale(image: Image.Image, scale: int) -> Image.Image:
    if scale not in (2, 4):
        raise ValueError("scale deve ser 2 ou 4")
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)


def rotate(image: Image.Image, angle: float) -> Image.Image:
    return image.rotate(max(-360, min(360, angle)), expand=True, resample=Image.Resampling.BICUBIC)


def flip(image: Image.Image, horizontal: bool) -> Image.Image:
    return ImageOps.mirror(image) if horizontal else ImageOps.flip(image)


def perspective(image: Image.Image, points: Iterable[Iterable[float]], output_size: tuple[int, int]) -> Image.Image:
    points = np.asarray(list(points), dtype=np.float32)
    if points.shape != (4, 2):
        raise ValueError("points deve conter exatamente quatro pontos [x, y]")
    width, height = output_size
    if width <= 0 or height <= 0:
        raise ValueError("output_size deve ser positivo")
    destination = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
    matrix = cv2.getPerspectiveTransform(points, destination)
    array = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGRA)
    warped = cv2.warpPerspective(array, matrix, (width, height), borderMode=cv2.BORDER_TRANSPARENT)
    return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA))


def remove_background(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError as exc:
        raise RuntimeError("Instale rembg e onnxruntime para usar remove-background") from exc
    result = remove(image)
    if isinstance(result, Image.Image):
        return result.convert("RGBA")
    return Image.open(io.BytesIO(result)).convert("RGBA")


def ocr(image: Image.Image):
    try:
        import easyocr
    except ImportError as exc:
        raise RuntimeError("Instale easyocr para usar OCR") from exc
    reader = easyocr.Reader(["pt", "en"], gpu=False)
    results = reader.readtext(np.asarray(image.convert("RGB")))
    return [{"box": box, "text": text, "confidence": float(confidence)} for box, text, confidence in results]


def main() -> None:
    parser = argparse.ArgumentParser(description="Python Image Lab")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--operation", required=True, choices=["upscale", "adjust", "rotate", "flip", "perspective", "remove-background", "ocr"])
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--angle", type=float, default=0)
    parser.add_argument("--brightness", type=float, default=1)
    parser.add_argument("--contrast", type=float, default=1)
    parser.add_argument("--saturation", type=float, default=1)
    parser.add_argument("--sharpness", type=float, default=1)
    parser.add_argument("--vertical", action="store_true")
    parser.add_argument("--points", help="JSON com quatro pontos: [[x,y],[x,y],[x,y],[x,y]]")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()
    image = load_image(args.input)
    if args.operation == "upscale":
        save_image(upscale(image, args.scale), args.output)
    elif args.operation == "adjust":
        save_image(adjust(image, args.brightness, args.contrast, args.saturation, args.sharpness), args.output)
    elif args.operation == "rotate":
        save_image(rotate(image, args.angle), args.output)
    elif args.operation == "flip":
        save_image(flip(image, not args.vertical), args.output)
    elif args.operation == "perspective":
        if not args.points or not args.width or not args.height:
            raise SystemExit("perspective exige --points, --width e --height")
        save_image(perspective(image, json.loads(args.points), (args.width, args.height)), args.output)
    elif args.operation == "remove-background":
        save_image(remove_background(image), args.output)
    else:
        Path(args.output).write_text(json.dumps(ocr(image), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
