from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
import os
import uuid
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "app" / "data" / "context"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

print(f"DEBUG: Upload directory is set to: {UPLOAD_DIR}")


@router.post("/context")
async def upload_context_file(file: UploadFile = File(...)):
    try:
        print(f"DEBUG: Received file upload request: {file.filename}")

        ext = Path(file.filename).suffix
        if not ext:
            ext = ".txt"  # 无后缀则默认为txt文件

        safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        print(f"DEBUG: Saving file to: {file_path}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"DEBUG: File saved successfully")

        return {
            "filename": safe_filename,
            "original_name": file.filename,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        print(f"ERROR: File upload failed: {e}")
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
