from __future__ import annotations

import asyncio
import json
import logging
import signal
import time

import redis
from config import get_settings
from jobs import process_operation, safe_job_error
from storage import LocalStorage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("canva-image-toolkit-worker")
settings = get_settings()
storage = LocalStorage(settings.storage_dir, settings.storage_ttl_seconds)
client = redis.from_url(settings.redis_url, decode_responses=True)
running = True


def stop(_signum: int, _frame: object) -> None:
    global running
    running = False


def run() -> None:
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    logger.info("worker started")
    while running:
        item = client.blpop("canva-image-toolkit:queue", timeout=5)
        if item is None:
            storage.cleanup()
            continue
        process_job(item[1])


def process_job(job_id: str) -> None:
    key = f"canva-image-toolkit:job:{job_id}"
    payload = client.hgetall(key)
    if not payload:
        return
    client.hset(key, mapping={"status": "running", "updated_at": str(int(time.time()))})
    input_key = payload.get("input_key", "")
    try:
        output, output_type = asyncio.run(
            process_operation(
                payload["operation"],
                storage.read(input_key),
                json.loads(payload.get("params", "{}")),
                settings,
            )
        )
        output_key = storage.write(
            output, ".json" if output_type == "application/json" else ".png"
        )
        client.hset(
            key,
            mapping={
                "status": "completed",
                "output_key": output_key,
                "output_type": output_type,
                "updated_at": str(int(time.time())),
            },
        )
    except Exception as error:
        logger.exception(
            "job failed id=%s operation=%s", job_id, payload.get("operation")
        )
        client.hset(
            key,
            mapping={
                "status": "failed",
                "error": safe_job_error(error),
                "updated_at": str(int(time.time())),
            },
        )
    finally:
        if input_key:
            storage.delete(input_key)


if __name__ == "__main__":
    run()
