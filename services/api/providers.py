from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
from config import Settings
from fastapi import HTTPException
from imaging import encode_png, upscale_lanczos
from PIL import Image


class ProviderUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderStatus:
    name: str
    enabled: bool
    detail: str


class RealEsrganProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def status(self) -> ProviderStatus:
        binary = self.settings.realesrgan_binary
        enabled = bool(binary and Path(binary).is_file())
        return ProviderStatus(
            "realesrgan",
            enabled,
            "binary configured" if enabled else "disabled; configure REALESRGAN_BINARY",
        )

    async def upscale(self, image: Image.Image, scale: int) -> Image.Image:
        status = self.status()
        if not status.enabled:
            if self.settings.upscaler_provider == "lanczos":
                return upscale_lanczos(image, scale, self.settings)
            raise ProviderUnavailable(status.detail)
        if scale not in (2, 4):
            raise HTTPException(400, "scale deve ser 2 ou 4")
        workdir = Path(tempfile.mkdtemp(prefix="realesrgan-"))
        try:
            source = workdir / "input.png"
            result = workdir / "output.png"
            source.write_bytes(encode_png(image, self.settings))
            command = [
                self.settings.realesrgan_binary,
                "-i",
                str(source),
                "-o",
                str(result),
                "-s",
                str(scale),
                "-t",
                str(self.settings.realesrgan_tile),
                "-n",
                self.settings.realesrgan_model,
                "-f",
                "png",
            ]
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.settings.request_timeout_seconds
            )
            if process.returncode != 0 or not result.is_file():
                message = stderr.decode("utf-8", errors="replace")[-500:]
                raise RuntimeError(f"Real-ESRGAN failed: {message}")
            with Image.open(result) as output:
                output.load()
                return output.convert("RGBA")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


class HuggingFaceBackgroundProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def status(self) -> ProviderStatus:
        enabled = bool(self.settings.huggingface_api_token)
        return ProviderStatus(
            "huggingface-background",
            enabled,
            "token configured"
            if enabled
            else "disabled; configure HUGGINGFACE_API_TOKEN",
        )

    async def remove(self, image_bytes: bytes) -> Image.Image:
        if not self.status().enabled:
            raise ProviderUnavailable(self.status().detail)
        url = f"https://router.huggingface.co/hf-inference/models/{self.settings.hf_background_model}"
        headers = {"Authorization": f"Bearer {self.settings.huggingface_api_token}"}
        timeout = httpx.Timeout(self.settings.hf_timeout_seconds)
        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(2):
                try:
                    response = await client.post(
                        url, headers=headers, content=image_bytes
                    )
                    if response.status_code in {429, 502, 503, 504} and attempt == 0:
                        await asyncio.sleep(1)
                        continue
                    response.raise_for_status()
                    with Image.open(BytesIO(response.content)) as result:
                        result.load()
                        return result.convert("RGBA")
                except (httpx.HTTPError, OSError) as exc:
                    last_error = exc
                    if attempt == 0:
                        await asyncio.sleep(1)
        raise RuntimeError("Hugging Face background removal failed") from last_error


class GoogleVisionOcrProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def status(self) -> ProviderStatus:
        credentials = self.settings.google_application_credentials
        enabled = bool(credentials and Path(credentials).is_file())
        return ProviderStatus(
            "google-vision-ocr",
            enabled,
            "credentials configured"
            if enabled
            else "disabled; configure GOOGLE_APPLICATION_CREDENTIALS",
        )

    async def detect(self, image_bytes: bytes) -> dict[str, Any]:
        if not self.status().enabled:
            raise ProviderUnavailable(self.status().detail)
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS",
            self.settings.google_application_credentials,
        )
        try:
            from google.cloud import vision
        except ImportError as exc:
            raise ProviderUnavailable(
                "install google-cloud-vision to enable OCR"
            ) from exc

        def call() -> dict[str, Any]:
            client = vision.ImageAnnotatorClient()
            response = client.text_detection(
                image=vision.Image(content=image_bytes),
                timeout=self.settings.vision_timeout_seconds,
            )
            if response.error.message:
                raise RuntimeError(response.error.message)
            annotations = []
            for item in response.text_annotations:
                annotations.append(
                    {
                        "text": item.description,
                        "vertices": [
                            {"x": vertex.x, "y": vertex.y}
                            for vertex in item.bounding_poly.vertices
                        ],
                    }
                )
            return {
                "text": annotations[0]["text"] if annotations else "",
                "annotations": annotations[1:],
            }

        return await asyncio.wait_for(
            asyncio.to_thread(call), timeout=self.settings.vision_timeout_seconds + 5
        )


def provider_statuses(settings: Settings) -> list[dict[str, Any]]:
    providers = [
        RealEsrganProvider(settings),
        HuggingFaceBackgroundProvider(settings),
        GoogleVisionOcrProvider(settings),
    ]
    return [status.__dict__ for status in (provider.status() for provider in providers)]


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
