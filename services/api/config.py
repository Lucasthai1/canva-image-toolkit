from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_auth_token: str = ""
    cors_origins: str = "http://localhost:5173"
    max_upload_bytes: int = 15 * 1024 * 1024
    max_pixels: int = 25_000_000
    max_output_pixels: int = 50_000_000
    request_timeout_seconds: int = 60
    max_concurrent_requests: int = 4
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    redis_url: str = "redis://redis:6379/0"
    storage_dir: Path = Path("/tmp/canva-image-toolkit")
    storage_ttl_seconds: int = 3600
    max_batch_files: int = 20
    upscaler_provider: str = "lanczos"
    realesrgan_binary: str = ""
    realesrgan_model: str = "realesrgan-x4plus"
    realesrgan_tile: int = 128
    huggingface_api_token: str = ""
    hf_background_model: str = "briaai/RMBG-1.4"
    hf_timeout_seconds: int = 60
    google_application_credentials: str = ""
    google_cloud_project: str = ""
    vision_timeout_seconds: int = 30

    @property
    def production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @field_validator(
        "max_upload_bytes",
        "max_pixels",
        "max_output_pixels",
        "request_timeout_seconds",
        "max_concurrent_requests",
        "rate_limit_requests",
        "rate_limit_window_seconds",
        "storage_ttl_seconds",
        "max_batch_files",
    )
    @classmethod
    def positive_integer(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be positive")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
