import os
from PIL import Image
from io import BytesIO

IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def _get_next_image_number(base_name: str, ext: str) -> int:
    existing = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().startswith(f"{base_name.lower()}_image_")
        and f.lower().endswith(f".{ext.lower()}")
    ]
    numbers = []
    for f in existing:
        try:
            num = int(f.split("_")[-1].split(".")[0])
            numbers.append(num)
        except ValueError:
            continue
    return max(numbers, default=0) + 1

def save_image(image_bytes: bytes, filename: str, ext: str = "png") -> str:
    base_name, _ = os.path.splitext(filename)
    base_name = os.path.basename(base_name)
    img_num = _get_next_image_number(base_name, ext)
    img_name = f"{base_name}_image_{img_num}.{ext}"
    img_path = os.path.join(IMAGE_DIR, img_name)

    with open(img_path, "wb") as f:
        f.write(image_bytes)

    # Validate image
    Image.open(BytesIO(image_bytes)).verify()

    return img_path

def make_image_record(image_bytes: bytes, filename: str, ext: str = "png") -> dict:
    img_path = save_image(image_bytes, filename, ext)
    return {
        "id": os.path.splitext(os.path.basename(img_path))[0],
        "path": img_path
    }
