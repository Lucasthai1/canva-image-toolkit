from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient
from main import app

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
    response = client.post("/v1/image/adjust?brightness=1.2&sharpness=2", files=image_file())
    assert response.status_code == 200

def test_rejects_wrong_type():
    response = client.post("/v1/image/upscale", files={"file": ("x.txt", b"hello", "text/plain")})
    assert response.status_code == 415
