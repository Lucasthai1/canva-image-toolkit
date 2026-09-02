from __future__ import annotations

import asyncio
import hmac
import json
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Annotated, Any

from config import get_settings
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from imaging import adjust_image, encode_png, read_upload
from jobs import SUPPORTED_OPERATIONS, JobStore, process_operation, public_job
from providers import ProviderUnavailable, provider_statuses
from redis.exceptions import RedisError
from storage import LocalStorage

settings = get_settings()
storage = LocalStorage(settings.storage_dir, settings.storage_ttl_seconds)
job_store = JobStore(settings)
semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
rate_buckets: dict[str, deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.production:
        if len(settings.api_auth_token) < 24:
            raise RuntimeError(
                "API_AUTH_TOKEN must contain at least 24 characters in production"
            )
        if not settings.parsed_cors_origins or "*" in settings.parsed_cors_origins:
            raise RuntimeError("CORS_ORIGINS must be explicit in production")
    storage.cleanup()
    yield
    await job_store.close()


app = FastAPI(
    title="Canva Image Toolkit API",
    version="1.0.0",
    docs_url=None if settings.production else "/docs",
    redoc_url=None if settings.production else "/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    allow_credentials=False,
)


@app.middleware("http")
async def security_and_limits(request: Request, call_next):
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex)[:64]
    if request.url.path not in {"/health", "/ready"}:
        early_response = authorize(request) or enforce_rate_limit(request)
        if early_response is not None:
            early_response.headers["X-Request-ID"] = request_id
            early_response.headers["Cache-Control"] = "no-store"
            early_response.headers["X-Content-Type-Options"] = "nosniff"
            return early_response
    try:
        async with semaphore:
            response = await asyncio.wait_for(
                call_next(request), timeout=settings.request_timeout_seconds
            )
    except TimeoutError:
        response = JSONResponse(
            {"detail": "Tempo limite da operação excedido"}, status_code=504
        )
    response.headers["X-Request-ID"] = request_id
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(ProviderUnavailable)
async def provider_unavailable(_request: Request, error: ProviderUnavailable):
    return JSONResponse({"detail": str(error)}, status_code=503)


@app.get("/health")
def health():
    return {"status": "ok", "service": "canva-image-toolkit", "version": app.version}


@app.get("/ready")
async def ready():
    try:
        redis_ready = await job_store.ping()
    except RedisError:
        redis_ready = False
    return JSONResponse(
        {
            "status": "ready" if redis_ready else "degraded",
            "redis": redis_ready,
            "providers": provider_statuses(settings),
        },
        status_code=200 if redis_ready else 503,
    )


@app.get("/v1/providers")
def providers():
    return {"providers": provider_statuses(settings)}


@app.post("/v1/image/adjust")
async def adjust(
    file: Annotated[UploadFile, File(...)],
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0,
):
    _, image = await read_upload(file, settings)
    return png_response(
        adjust_image(image, brightness, contrast, saturation, sharpness)
    )


@app.post("/v1/image/flip")
async def flip(file: Annotated[UploadFile, File(...)], horizontal: bool = True):
    return await image_operation("flip", file, {"horizontal": horizontal})


@app.post("/v1/image/rotate")
async def rotate(file: Annotated[UploadFile, File(...)], angle: float = 0):
    return await image_operation("rotate", file, {"angle": angle})


@app.post("/v1/image/perspective")
async def perspective(
    file: Annotated[UploadFile, File(...)],
    points: Annotated[str, Form(...)],
    width: Annotated[int, Form(...)],
    height: Annotated[int, Form(...)],
):
    try:
        parsed_points = json.loads(points)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "points deve ser JSON válido") from exc
    return await image_operation(
        "perspective", file, {"points": parsed_points, "width": width, "height": height}
    )


@app.post("/v1/image/upscale")
async def upscale(file: Annotated[UploadFile, File(...)], scale: int = 2):
    return await image_operation("upscale", file, {"scale": scale})


@app.post("/v1/image/remove-background")
async def remove_background(file: Annotated[UploadFile, File(...)]):
    return await image_operation("remove-background", file, {})


@app.post("/v1/image/ocr")
async def ocr(file: Annotated[UploadFile, File(...)]):
    data, _ = await read_upload(file, settings)
    output, output_type = await process_operation("ocr", data, {}, settings)
    return Response(output, media_type=output_type)


@app.post("/v1/jobs", status_code=202)
async def create_job(
    operation: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
    params: Annotated[str, Form()] = "{}",
):
    if operation not in SUPPORTED_OPERATIONS:
        raise HTTPException(400, "Operação de job não suportada")
    data, _ = await read_upload(file, settings)
    job_id = await enqueue_with_cleanup(operation, data, parse_params(params))
    payload = await job_store.get(job_id)
    if payload is None:
        raise HTTPException(503, "Fila temporariamente indisponível")
    return public_job(payload)


@app.post("/v1/batches", status_code=202)
async def create_batch(
    operation: Annotated[str, Form(...)],
    files: Annotated[list[UploadFile], File(...)],
    params: Annotated[str, Form()] = "{}",
):
    if operation not in SUPPORTED_OPERATIONS:
        raise HTTPException(400, "Operação de job não suportada")
    if not files or len(files) > settings.max_batch_files:
        raise HTTPException(
            400, f"O lote deve conter de 1 a {settings.max_batch_files} arquivos"
        )
    parsed_params = parse_params(params)
    jobs = []
    for file in files:
        data, _ = await read_upload(file, settings)
        jobs.append(await enqueue_with_cleanup(operation, data, parsed_params))
    return {"operation": operation, "jobs": jobs}


@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str):
    payload = await job_store.get(job_id)
    if payload is None:
        raise HTTPException(404, "Job não encontrado")
    return public_job(payload)


@app.get("/v1/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    payload = await job_store.get(job_id)
    if payload is None:
        raise HTTPException(404, "Job não encontrado")
    if payload.get("status") != "completed" or not payload.get("output_key"):
        raise HTTPException(409, "Resultado ainda não está disponível")
    try:
        content = storage.read(payload["output_key"])
    except FileNotFoundError as exc:
        raise HTTPException(410, "Resultado expirado") from exc
    return Response(
        content, media_type=payload.get("output_type", "application/octet-stream")
    )


async def image_operation(
    operation: str, file: UploadFile, params: dict[str, Any]
) -> Response:
    data, _ = await read_upload(file, settings)
    output, output_type = await process_operation(operation, data, params, settings)
    return Response(output, media_type=output_type)


async def enqueue_with_cleanup(
    operation: str, data: bytes, params: dict[str, Any]
) -> str:
    input_key = storage.write(data, ".bin")
    try:
        return await job_store.enqueue(operation, input_key, params)
    except RedisError as exc:
        storage.delete(input_key)
        raise HTTPException(503, "Fila temporariamente indisponível") from exc


def png_response(image) -> Response:
    return Response(encode_png(image, settings), media_type="image/png")


def parse_params(value: str) -> dict[str, Any]:
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "params deve ser JSON válido") from exc
    if not isinstance(payload, dict):
        raise HTTPException(400, "params deve ser um objeto JSON")
    return payload


def authorize(request: Request) -> Response | None:
    if not settings.api_auth_token:
        return None
    supplied = request.headers.get("authorization", "")
    if not hmac.compare_digest(supplied, f"Bearer {settings.api_auth_token}"):
        return JSONResponse(
            {"detail": "Token de API inválido"},
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return None


def enforce_rate_limit(request: Request) -> Response | None:
    forwarded = request.headers.get("x-forwarded-for", "")
    client = (
        forwarded.split(",", 1)[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )
    now = time.monotonic()
    bucket = rate_buckets[client]
    threshold = now - settings.rate_limit_window_seconds
    while bucket and bucket[0] <= threshold:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_requests:
        return JSONResponse(
            {"detail": "Limite de requisições excedido"}, status_code=429
        )
    bucket.append(now)
    return None
