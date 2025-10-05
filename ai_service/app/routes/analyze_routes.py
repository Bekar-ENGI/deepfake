import os
import orjson
from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import JSONResponse

from app.api.ApiResponse import ApiResponse
from app.helpers.cloud_helper import cloud_init 
from app.services.chunk_service import chunk_text_from_json
from app.interceptors.text_interceptor import analyze_text
from app.interceptors.Image_interceptor import image_inspector

OUTPUT_DIR = "output"
IMAGES_DIR = "images"

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.get("/")
def analyze_file(request: Request, filename: str = Query(..., description="Base filename (with or without .json)")):
    """
    Analyze chunks of text and images from a processed JSON file.
    Automatically chunks JSON if 'chunks' key is missing.
    Returns actual chunk text along with text and image analysis results.
    """
    # Normalize filename
    if not filename.lower().endswith(".json"):
        filename = f"{filename}.json"
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in {OUTPUT_DIR}/")

    # Load JSON file
    try:
        with open(file_path, "rb") as f:
            data = orjson.loads(f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {filename}: {str(e)}")

    # Automatically chunk if missing
    if "chunks" not in data:
        try:
            data = chunk_text_from_json(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to chunk JSON: {str(e)}")

    results = []

    for idx, chunk in enumerate(data["chunks"]):
        # Use the key from chunk_text_from_json ("chunk")
        chunk_text = chunk.get("chunk", "")

        chunk_result = {
            "chunk_index": idx,
            "chunk_text": chunk_text,
            "text_analysis": None,
            "image_analysis": []
        }

        # --- Text analysis ---
        if chunk_text.strip():
            chunk_result["text_analysis"] = analyze_text(chunk_text)

        # --- Image analysis ---
        images = chunk.get("images", [])
        for img_info in images:
            # Handle dict or str
            if isinstance(img_info, dict):
                img_path = img_info.get("path")
            elif isinstance(img_info, str):
                img_path = os.path.join(IMAGES_DIR, img_info)
            else:
                img_path = None

            if img_path and os.path.exists(img_path):
                try:
                    img_result = image_inspector(img_path)
                except Exception as e:
                    img_result = {"error": f"Failed to analyze image: {str(e)}", "file": img_info}
            else:
                img_result = {"error": "Image not found", "file": img_info}

            # Use stringified key for consistency
            chunk_result["image_analysis"].append({str(img_info): img_result})

        results.append(chunk_result)

    cloud_intializer = " ".join([ chunk.get("chunk", "") for idx, chunk in enumerate(data.get("chunks", [])) if idx < 1 ])


    verdict = cloud_init(cloud_intializer)

    

    return JSONResponse(ApiResponse(
        status="success",
        message=f"Analysis completed for {filename}",
        data={
            "filename": filename,
            "results": results,
            "Verdict" : verdict
        },
        request=request
    ))
