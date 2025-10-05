from datetime import datetime
from fastapi import Request

def ApiResponse(status: str, message: str, data: any, request: Request) -> dict:
    """
    Standardized API response format.
    """
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "path": request.url.path,
    }
