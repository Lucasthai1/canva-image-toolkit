import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from image_toolkit import adjust, flip, perspective, rotate, save_image, upscale


def sample():
    return Image.new("RGBA", (8, 6), (255, 0, 0, 255))


def test_upscale():
    assert upscale(sample(), 2).size == (16, 12)


def test_adjust_preserves_size():
    assert adjust(sample(), brightness=1.2).size == (8, 6)


def test_rotate_expands():
    assert rotate(sample(), 10).size[0] > 8


def test_flip_preserves_size():
    assert flip(sample(), True).size == (8, 6)


def test_perspective():
    result = perspective(sample(), [[0, 0], [7, 0], [7, 5], [0, 5]], (20, 10))
    assert result.size == (20, 10)


def test_save_jpeg(tmp_path):
    target = tmp_path / "result.jpg"
    save_image(sample(), target)
    assert target.exists()
    assert Image.open(target).mode == "RGB"
