from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
import os
import uuid
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

# Use absolute path resolution
# E:\TraePrograms\Agent
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "app" / "data" / "context"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

print(f"DEBUG: Upload directory is set to: {UPLOAD_DIR}")


@router.post("/context")
async def upload_context_file(file: UploadFile = File(...)):
    try:
        print(f"DEBUG: Received file upload request: {file.filename}")

        # Generate a safe filename to prevent overwrites or traversal
        # We keep the original extension
        ext = Path(file.filename).suffix
        if not ext:
            ext = ".txt"  # Default to txt if no extension

        # Use UUID to ensure uniqueness, or keep original name if preferred?
        # User might want to see the name they uploaded.
        # Let's use original filename but sanitize it, or prepend UUID.
        # Simple approach: Prepend UUID to ensure uniqueness but keep original name for reference
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
