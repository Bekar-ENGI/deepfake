import os
from docx import Document
from app.services.image_service import make_image_record
from app.utils.json_utils import save_json

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_docx_content(file_path: str) -> str:
    """
    Extract text + images from DOCX and save JSON. Returns JSON path.
    """
    if not file_path.endswith(".docx"):
        raise ValueError("File is not a DOCX")

    filename = os.path.splitext(os.path.basename(file_path))[0]
    doc = Document(file_path)
    pages_data = []
    current_page = {"page": 1, "text": [], "images": []}
    page_number = 1

    for para in doc.paragraphs:
        if para.runs:
            for run in para.runs:
                for br in run._element.findall(".//w:br", run._element.nsmap):
                    if br.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type") == "page":
                        pages_data.append({
                            "page": page_number,
                            "text": "\n".join(current_page["text"]).strip(),
                            "images": current_page["images"]
                        })
                        page_number += 1
                        current_page = {"page": page_number, "text": [], "images": []}

        if para.text.strip():
            current_page["text"].append(para.text.strip())

        for run in para.runs:
            if run._element.xpath(".//a:blip"):
                for blip in run._element.xpath(".//a:blip"):
                    rId = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                    image_part = doc.part.related_parts[rId]
                    image_bytes = image_part.blob
                    current_page["images"].append(make_image_record(image_bytes, filename=filename, ext="png"))

    if current_page["text"] or current_page["images"]:
        pages_data.append({
            "page": page_number,
            "text": "\n".join(current_page["text"]).strip(),
            "images": current_page["images"]
        })

    return save_json(pages_data, f"{filename}.json")
