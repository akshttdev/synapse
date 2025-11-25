# backend/services/upload_service.py
import uuid
from pathlib import Path
import aiofiles
import logging
from functools import lru_cache
from typing import Dict, Optional

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class UploadService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_and_process(self, file, media_type: str, metadata: Optional[str] = None) -> Dict:
        media_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix or ""
        out_path = self.upload_dir / f"{media_id}{ext}"

        # save file locally
        async with aiofiles.open(out_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved upload to {out_path}")

        # Import orchestrator
        from workers.worker_tasks import process_and_embed

        # enqueue
        task = process_and_embed.delay(media_id=media_id, source_url=str(out_path), media_type=media_type, storage_hint="s3")
        logger.info(f"Enqueued orchestrator task: {task.id}")

        return {
            "media_id": media_id,
            "task_id": task.id,
            "status": "processing",
            "message": "Upload accepted and processing started"
        }

    async def get_task_status(self, task_id: str) -> Dict:
        from celery.result import AsyncResult
        res = AsyncResult(task_id)
        return {"task_id": task_id, "status": res.state, "result": res.result if res.ready() else None}


def get_upload_service():
    return UploadService()
