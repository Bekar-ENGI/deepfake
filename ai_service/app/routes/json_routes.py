import os
import orjson
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from app.api.ApiResponse import ApiResponse  

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

router = APIRouter( tags=["load json"])

@router.get("/get_files")
def get_json_files(request: Request, file_name: str | None = Query(default=None, description="Optional filename (with or without .json)")):
    if file_name:
        # Normalize filename (allow with or without .json)
        if not file_name.lower().endswith(".json"):
            file_name = f"{file_name}.json"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in output/")

        try:
            with open(file_path, "rb") as f:
                data = orjson.loads(f.read())
            return JSONResponse(ApiResponse("success", f"File '{file_name}' loaded", data, request))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading {file_name}: {str(e)}")

    # No param → return all JSONs
    all_data = []
    for file in os.listdir(OUTPUT_DIR):
        if file.lower().endswith(".json"):
            file_path = os.path.join(OUTPUT_DIR, file)
            try:
                with open(file_path, "rb") as f:
                    data = orjson.loads(f.read())
                all_data.append({"file_name": file, "data": data})
            except Exception:
                continue

    return JSONResponse(ApiResponse("success", "All JSON files loaded", all_data, request))
