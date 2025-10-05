import os
import numpy as np
from PIL import Image
import exifread

# ------------------ Loaders ------------------

def load_image(path: str) -> Image.Image:
    """Load an image from a given file path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path)

def get_exif_data(path: str) -> dict:
    """Extract EXIF metadata from an image file."""
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        return {tag: str(tags[tag]) for tag in tags}
    except Exception:
        return {}

# ------------------ Checks ------------------

def check_metadata(exif: dict, filename: str = "") -> tuple[int, list[str]]:
    suspicious_tags = ['Software', 'Image Description']
    missing_camera_tags = ['Make', 'Model']
    reasons = []
    score = 0

    if not exif:
        score = 1
        reasons.append("No EXIF metadata")
        return score, reasons

    if exif.get("EXIF LightSource", "").lower() == "unknown" and exif.get("Image Orientation", "0") == "0":
        score = 1
        reasons.append("Suspicious EXIF (LightSource=Unknown, Orientation=0)")

    for tag in suspicious_tags:
        if tag in exif and any(ai in exif[tag].lower() for ai in ["ai", "dall", "meta", "stable", "midjourney"]):
            score = 1
            reasons.append(f"Suspicious EXIF tag: {tag} = {exif[tag]}")

    if any(tag not in exif for tag in missing_camera_tags):
        score = 1
        reasons.append("Missing essential camera tags (Make/Model)")

    if any(ai in filename.lower() for ai in ["meta", "dalle", "ai", "stable", "mj"]):
        score = 1
        reasons.append("Filename suggests AI origin")

    return score, reasons

def check_entropy(image: Image.Image) -> float:
    grayscale = image.convert('L')
    pixels = np.array(grayscale).flatten()
    histogram = np.histogram(pixels, bins=256)[0]
    probs = histogram / np.sum(histogram)
    entropy = -np.sum([p * np.log2(p) for p in probs if p > 0])
    return float(entropy)

def check_color_distribution(image: Image.Image) -> float:
    pixels = np.array(image)
    if len(pixels.shape) == 3:  # RGB
        r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
        return float(np.mean([np.std(r), np.std(g), np.std(b)]))
    return 0.0

def check_blockiness(image: Image.Image) -> float:
    grayscale = image.convert('L')
    pixels = np.array(grayscale)
    h, w = pixels.shape
    blocks = []
    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            block = pixels[i:i + 8, j:j + 8]
            blocks.append(np.std(block))
    return float(np.mean(blocks)) if blocks else 0.0

# ------------------ Main Inspector ------------------

def image_inspector(img_input) -> dict:
    """
    Run AI vs Human heuristic detection on an image.
    img_input: str (path) or dict with {"path": "..."}
    """
    if isinstance(img_input, dict):
        path = img_input.get("path", "")
        name = os.path.basename(path)
    else:
        path = img_input
        name = os.path.basename(path)

    try:
        image = load_image(path)
    except FileNotFoundError:
        return {"error": "Image not found", "file": path}

    exif = get_exif_data(path)

    flags = []
    metrics = {}

    # --- Run checks ---
    meta_score, meta_reasons = check_metadata(exif, name)
    entropy = check_entropy(image)
    color_std = check_color_distribution(image)
    blockiness = check_blockiness(image)

    metrics.update({
        "entropy": round(entropy, 2),
        "color_std": round(color_std, 2),
        "blockiness": round(blockiness, 2),
        "metadata_score": meta_score
    })

    # Collect flags for suspicious metadata or metrics
    if meta_score > 0:
        flags.extend(meta_reasons)

    weights = {"metadata": 0.25, "entropy": 0.25, "color_std": 0.25, "blockiness": 0.25}
    score = 0.0

    if entropy < 5.0:
        score += weights["entropy"]
        flags.append("Low entropy (possible synthetic texture)")

    if color_std < 20:
        score += weights["color_std"]
        flags.append("Low color variation (possible AI palette)")

    if image.format != "PNG" and blockiness < 5:
        score += weights["blockiness"]
        flags.append("Low JPEG blockiness (may lack natural compression)")

    return {
        "confidence": round(score, 2),
        "flags": flags,
        "metrics": metrics,
        "exif": exif
    }
