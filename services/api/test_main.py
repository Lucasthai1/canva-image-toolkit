import asyncio
from io import BytesIO

from fastapi.testclient import TestClient
from jobs import process_operation
from main import app, settings
from PIL import Image
from storage import LocalStorage

client = TestClient(app)


def image_file(size=(8, 6)):
    image = Image.new("RGBA", size, (255, 0, 0, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return {"file": ("test.png", buffer, "image/png")}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upscale():
    response = client.post("/v1/image/upscale?scale=2", files=image_file())
    assert response.status_code == 200
    result = Image.open(BytesIO(response.content))
    assert result.size == (16, 12)


def test_adjust():
    response = client.post(
        "/v1/image/adjust?brightness=1.2&sharpness=2", files=image_file()
    )
    assert response.status_code == 200


def test_rejects_wrong_type():
    response = client.post(
        "/v1/image/upscale", files={"file": ("x.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 415


def test_rejects_declared_mime_mismatch():
    response = client.post(
        "/v1/image/upscale",
        files={"file": ("x.jpg", image_file()["file"][1], "image/jpeg")},
    )
    assert response.status_code == 415


def test_perspective():
    response = client.post(
        "/v1/image/perspective",
        files=image_file(),
        data={"points": "[[0,0],[7,0],[7,5],[0,5]]", "width": "8", "height": "6"},
    )
    assert response.status_code == 200
    assert Image.open(BytesIO(response.content)).size == (8, 6)


def test_invalid_perspective_json():
    response = client.post(
        "/v1/image/perspective",
        files=image_file(),
        data={"points": "not-json", "width": "8", "height": "6"},
    )
    assert response.status_code == 400


def test_disabled_provider_is_explicit():
    original = settings.huggingface_api_token
    settings.huggingface_api_token = ""
    try:
        response = client.post("/v1/image/remove-background", files=image_file())
        assert response.status_code == 503
        assert "HUGGINGFACE_API_TOKEN" in response.json()["detail"]
    finally:
        settings.huggingface_api_token = original


def test_bearer_authentication():
    original = settings.api_auth_token
    settings.api_auth_token = "a" * 32
    try:
        assert client.get("/v1/providers").status_code == 401
        response = client.get(
            "/v1/providers",
            headers={"Authorization": f"Bearer {settings.api_auth_token}"},
        )
        assert response.status_code == 200
    finally:
        settings.api_auth_token = original


def test_process_operation_adjust():
    source = image_file()["file"][1].getvalue()
    output, mime = asyncio.run(
        process_operation("adjust", source, {"brightness": 1.2}, settings)
    )
    assert mime == "image/png"
    assert Image.open(BytesIO(output)).size == (8, 6)


def test_local_storage_uses_random_keys_and_ttl(tmp_path):
    storage = LocalStorage(tmp_path, ttl_seconds=1)
    key = storage.write(b"private", ".bin")
    assert key != "private"
    assert storage.read(key) == b"private"
    assert storage.cleanup(now=(tmp_path / key).stat().st_mtime + 2) == 1
    assert not (tmp_path / key).exists()


def test_batch_limit_is_enforced_before_queue_access():
    files = [
        ("files", (f"{index}.png", image_file()["file"][1].getvalue(), "image/png"))
        for index in range(settings.max_batch_files + 1)
    ]
    response = client.post(
        "/v1/batches", data={"operation": "adjust", "params": "{}"}, files=files
    )
    assert response.status_code == 400
