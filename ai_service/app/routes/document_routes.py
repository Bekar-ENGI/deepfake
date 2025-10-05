import os
import time
from fastapi import APIRouter, UploadFile, HTTPException, Request
from app.services.chunk_service import chunk_text_from_json
from app.services.docx_service import extract_docx_content
from app.services.pdf_service import extract_pdf_content
from app.utils.json_utils import load_json
from app.utils.file_utils import save_file
from app.api.ApiResponse import ApiResponse

router = APIRouter(prefix="/document", tags=["document"])

@router.post("/upload")
async def upload_document(request: Request, file: UploadFile, userId: str, username: str, max_words: int = 450):
    """
    Upload a PDF or DOCX, rename it, extract content, chunk text, and return chunks + images.
    """
    try:
        # Extract original filename and extension
        file_name, file_ext = os.path.splitext(file.filename)
        file_ext = file_ext.lower()

        if file_ext not in [".pdf", ".docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Rename file before saving
        new_filename = f"{file_name}_{username}_{userId}{file_ext}"
        file_path = await save_file(file, custom_filename=new_filename)

        # Extract content
        if file_ext == ".pdf":
            output_json_path = extract_pdf_content(file_path)
            time.sleep(0.9)
            json_data = load_json(output_json_path)

        elif file_ext == ".docx":
            output_json_path = extract_docx_content(file_path)
            time.sleep(0.9)
            json_data = load_json(output_json_path)

        # Chunk text
        chunks = chunk_text_from_json(output_json_path, max_words=max_words)
        time.sleep(0.9)

        

        # Prepare response
        response_data = {
            "file_name": new_filename,
            "file_extension": file_ext,
            "chunks": chunks["chunks"],
            "images": chunks["images"]
        }

        return ApiResponse("success", f"{file_ext.upper()} processed successfully", response_data, request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")