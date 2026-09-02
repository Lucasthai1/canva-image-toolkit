from __future__ import annotations

import json
import time
import uuid
from typing import Any

import redis.asyncio as redis_async
from config import Settings
from fastapi import HTTPException
from imaging import adjust_image, decode_image, encode_png, perspective_image
from PIL import Image, ImageOps
from providers import (
    GoogleVisionOcrProvider,
    HuggingFaceBackgroundProvider,
    ProviderUnavailable,
    RealEsrganProvider,
    json_bytes,
)

SUPPORTED_OPERATIONS = {
    "adjust",
    "flip",
    "rotate",
    "perspective",
    "upscale",
    "remove-background",
    "ocr",
}


class JobStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis = redis_async.from_url(settings.redis_url, decode_responses=True)

    async def ping(self) -> bool:
        return bool(await self.redis.ping())

    async def enqueue(
        self, operation: str, input_key: str, params: dict[str, Any]
    ) -> str:
        if operation not in SUPPORTED_OPERATIONS:
            raise HTTPException(400, "Operação de job não suportada")
        job_id = uuid.uuid4().hex
        key = self._key(job_id)
        now = str(int(time.time()))
        await self.redis.hset(
            key,
            mapping={
                "id": job_id,
                "operation": operation,
                "status": "queued",
                "input_key": input_key,
                "params": json.dumps(params, separators=(",", ":")),
                "created_at": now,
                "updated_at": now,
                "error": "",
                "output_key": "",
                "output_type": "",
            },
        )
        await self.redis.expire(key, self.settings.storage_ttl_seconds * 2)
        await self.redis.rpush("canva-image-toolkit:queue", job_id)
        return job_id

    async def get(self, job_id: str) -> dict[str, str] | None:
        if len(job_id) != 32 or any(
            character not in "0123456789abcdef" for character in job_id
        ):
            return None
        payload = await self.redis.hgetall(self._key(job_id))
        return payload or None

    async def close(self) -> None:
        await self.redis.aclose()

    @staticmethod
    def _key(job_id: str) -> str:
        return f"canva-image-toolkit:job:{job_id}"


async def process_operation(
    operation: str, image_bytes: bytes, params: dict[str, Any], settings: Settings
) -> tuple[bytes, str]:
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError("unsupported operation")
    if operation == "remove-background":
        result = await HuggingFaceBackgroundProvider(settings).remove(image_bytes)
        return encode_png(result, settings), "image/png"
    if operation == "ocr":
        return json_bytes(
            await GoogleVisionOcrProvider(settings).detect(image_bytes)
        ), "application/json"
    image = decode_image(image_bytes, settings)
    if operation == "adjust":
        result = adjust_image(
            image,
            _float(params, "brightness", 1),
            _float(params, "contrast", 1),
            _float(params, "saturation", 1),
            _float(params, "sharpness", 1),
        )
    elif operation == "flip":
        result = (
            ImageOps.mirror(image)
            if bool(params.get("horizontal", True))
            else ImageOps.flip(image)
        )
    elif operation == "rotate":
        result = image.rotate(
            max(-360, min(360, _float(params, "angle", 0))),
            expand=True,
            resample=Image.Resampling.BICUBIC,
        )
    elif operation == "perspective":
        points = params.get("points")
        if not isinstance(points, list):
            raise ValueError("points is required")
        result = perspective_image(
            image,
            points,
            (int(params.get("width", 0)), int(params.get("height", 0))),
            settings,
        )
    else:
        result = await RealEsrganProvider(settings).upscale(
            image, int(params.get("scale", 2))
        )
    return encode_png(result, settings), "image/png"


def public_job(payload: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": payload["id"],
        "operation": payload["operation"],
        "status": payload["status"],
        "created_at": int(payload["created_at"]),
        "updated_at": int(payload["updated_at"]),
    }
    if payload.get("error"):
        result["error"] = payload["error"]
    if payload.get("output_key"):
        result.update(
            result_url=f"/v1/jobs/{payload['id']}/result",
            output_type=payload.get("output_type", "application/octet-stream"),
        )
    return result


def safe_job_error(error: Exception) -> str:
    if isinstance(error, ProviderUnavailable):
        return str(error)
    if isinstance(error, HTTPException):
        return str(error.detail)
    if isinstance(error, (ValueError, TypeError)):
        return str(error)[:300]
    return "Falha interna ao processar o job"


def _float(params: dict[str, Any], name: str, default: float) -> float:
    return float(params.get(name, default))
