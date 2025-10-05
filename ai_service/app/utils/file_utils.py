import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_file(file: UploadFile, custom_filename: str = None) -> str:
    """
    Save uploaded file to UPLOAD_DIR. Handles duplicate names.
    If custom_filename is provided, use it instead of file.filename.
    Returns the full path.
    """
    filename = custom_filename if custom_filename else file.filename
    name, ext = os.path.splitext(filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    i = 1
    while os.path.exists(file_path):
        new_filename = f"{name}_duplicate_{i}{ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        i += 1

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path
