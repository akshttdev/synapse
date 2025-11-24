# backend/api/routes/upload.py
"""
Upload endpoints for media files
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from services.upload_service import UploadService, get_upload_service

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    media_id: str
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


@router.post("/", response_model=UploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = Form(...),
    metadata: Optional[str] = Form(None),
    upload_service: UploadService = Depends(get_upload_service)
):
    """
    Upload media file for indexing
    
    - **file**: Media file (image/audio/video)
    - **media_type**: One of: image, audio, video
    - **metadata**: Optional JSON metadata
    """
    try:
        # Validate media type
        if media_type not in ["image", "audio", "video"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid media_type: {media_type}"
            )
        
        # Validate file type
        content_type = file.content_type or ""
        
        if media_type == "image" and not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image file")
        elif media_type == "audio" and not content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        elif media_type == "video" and not content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Invalid video file")
        
        # Process upload
        result = await upload_service.upload_and_process(
            file=file,
            media_type=media_type,
            metadata=metadata
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    upload_service: UploadService = Depends(get_upload_service)
):
    """
    Check upload processing status
    
    - **task_id**: Celery task ID from upload response
    """
    try:
        status = await upload_service.get_task_status(task_id)
        return status
    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))