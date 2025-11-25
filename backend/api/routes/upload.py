# backend/api/routes/upload.py
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
from services.upload_service import get_upload_service, UploadService

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    media_id: str
    task_id: str
    status: str
    message: str


@router.post("/", response_model=UploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = Form(...),
    metadata: Optional[str] = Form(None),
    upload_service: UploadService = Depends(get_upload_service)
):
    try:
        if media_type not in ("image", "audio", "video"):
            raise HTTPException(status_code=400, detail="Invalid media_type")

        # Validate MIME type
        ct = file.content_type or ""
        if media_type == "image" and not ct.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image file")
        if media_type == "audio" and not ct.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        if media_type == "video" and not ct.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid video file")

        result = await upload_service.upload_and_process(file=file, media_type=media_type, metadata=metadata)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def status(task_id: str, upload_service: UploadService = Depends(get_upload_service)):
    try:
        status = await upload_service.get_task_status(task_id)
        return status
    except Exception as e:
        logger.exception("Status check failed")
        raise HTTPException(status_code=500, detail=str(e))
