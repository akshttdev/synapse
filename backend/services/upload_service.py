# backend/services/upload_service.py
"""
Upload service - handles file uploads and triggers processing
"""

import uuid
import tempfile
from pathlib import Path
from typing import Dict
import aiofiles
from fastapi import UploadFile
from celery.result import AsyncResult
import logging
from functools import lru_cache

from core.config import get_settings

logger = logging.getLogger(__name__)


class UploadService:
    """Handle media uploads"""
    
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(tempfile.gettempdir()) / "scalesearch_uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_and_process(
        self,
        file: UploadFile,
        media_type: str,
        metadata: str = None
    ) -> Dict:
        """
        Upload file and trigger processing
        
        Args:
            file: Uploaded file
            media_type: Media type (image/audio/video)
            metadata: Optional JSON metadata
        
        Returns:
            Upload response with task ID
        """
        # Generate unique ID
        media_id = str(uuid.uuid4())
        
        # Save file temporarily
        file_ext = Path(file.filename).suffix
        temp_path = self.upload_dir / f"{media_id}{file_ext}"
        
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"✓ Saved upload to {temp_path}")
        
        # Trigger Celery worker
        from workers.worker_tasks import process_and_embed
        
        task = process_and_embed.delay(
            media_id=media_id,
            source_url=str(temp_path),  # Local path for now
            media_type=media_type,
            storage_hint="r2"
        )
        
        logger.info(f"✓ Triggered processing task: {task.id}")
        
        return {
            "media_id": media_id,
            "task_id": task.id,
            "status": "processing",
            "message": f"File uploaded and processing started"
        }
    
    async def get_task_status(self, task_id: str) -> Dict:
        """Check Celery task status"""
        result = AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.state,
            "result": result.result if result.ready() else None
        }


@lru_cache()
def get_upload_service() -> UploadService:
    """Get cached upload service instance"""
    return UploadService()