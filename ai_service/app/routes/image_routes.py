import os
from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.api.ApiResponse import ApiResponse  # Global API response

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/")
def get_images(request: Request, filename: str | None = Query(default=None, description="Base filename to filter (without _image_X)")):
    """
    List all available images or filter by base filename.
    """
    if not os.path.exists(IMAGES_DIR):
        return JSONResponse(ApiResponse(
            status="error",
            message="Images directory not found",
            data=None,
            request=request
        ), status_code=404)

    files = os.listdir(IMAGES_DIR)
    images = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"))]

    if filename:
        images = [img for img in images if img.startswith(f"{filename}_image_")]

    if not images:
        return JSONResponse(ApiResponse(
            status="error",
            message=f"No images found for '{filename}'" if filename else "No images found",
            data=None,
            request=request
        ), status_code=404)

    base_url = str(request.base_url).rstrip("/")
    image_urls = [f"{base_url}/images/file/{img}" for img in images]

    return JSONResponse(ApiResponse(
        status="success",
        message="Images retrieved successfully",
        data={"images": image_urls},
        request=request
    ))


@router.get("/file/{image_name}")
def get_image(request: Request, image_name: str):
    """
    Serve an image file by its name.
    """
    image_path = os.path.join(IMAGES_DIR, image_name)

    if not os.path.exists(image_path):
        return JSONResponse(ApiResponse(
            status="error",
            message=f"Image '{image_name}' not found",
            data=None,
            request=request
        ), status_code=404)

    return FileResponse(image_path)
