from __future__ import annotations

import os
import time
import uuid
from pathlib import Path


class LocalStorage:
    def __init__(self, root: Path, ttl_seconds: int):
        self.root = root
        self.ttl_seconds = ttl_seconds
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def write(self, data: bytes, suffix: str = ".bin") -> str:
        safe_suffix = suffix if suffix in {".png", ".json", ".bin"} else ".bin"
        name = f"{uuid.uuid4().hex}{safe_suffix}"
        target = self.root / name
        target.write_bytes(data)
        try:
            os.chmod(target, 0o600)
        except OSError:
            pass
        return name

    def read(self, name: str) -> bytes:
        target = self._resolve(name)
        return target.read_bytes()

    def delete(self, name: str) -> None:
        self._resolve(name).unlink(missing_ok=True)

    def cleanup(self, now: float | None = None) -> int:
        threshold = (now or time.time()) - self.ttl_seconds
        removed = 0
        for target in self.root.iterdir():
            if target.is_file() and target.stat().st_mtime < threshold:
                target.unlink(missing_ok=True)
                removed += 1
        return removed

    def _resolve(self, name: str) -> Path:
        if not name or Path(name).name != name:
            raise ValueError("invalid storage key")
        target = (self.root / name).resolve()
        if target.parent != self.root.resolve():
            raise ValueError("invalid storage key")
        return target
