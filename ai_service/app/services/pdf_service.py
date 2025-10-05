import fitz  # PyMuPDF
import os
from app.services.image_service import make_image_record
from app.utils.json_utils import save_json

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_pdf_content(file_path: str) -> str:
    """
    Extract text + images from PDF and save JSON. Returns JSON path.
    """
    doc = fitz.open(file_path)
    pages_data = []
    filename = os.path.splitext(os.path.basename(file_path))[0]

    for i, page in enumerate(doc):
        page_text = page.get_text("text")
        images = []

        for _, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            images.append(make_image_record(img_bytes, filename=filename, ext=img_ext))

        pages_data.append({
            "page": i + 1,
            "text": page_text.strip(),
            "images": images
        })

    return save_json(pages_data, f"{filename}.json")
