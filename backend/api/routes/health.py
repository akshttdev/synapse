# backend/api/routes/health.py
from fastapi import APIRouter
from datetime import datetime
import logging
import torch

from core.config import get_settings
from core.cache import get_cache_manager
from core.qdrant_client import get_qdrant_client
from core.storage import _s3_client

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_check():
    checks = {}
    # Redis
    try:
        checks["redis"] = "ok" if get_cache_manager().ping() else "error"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    # Qdrant
    try:
        client = get_qdrant_client(settings.QDRANT_URL, settings.QDRANT_API_KEY)
        # a simple request
        _ = client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {e}"
    # S3
    try:
        s3 = _s3_client()
        bucket = settings.AWS_S3_BUCKET
        s3.head_bucket(Bucket=bucket)
        checks["s3"] = "ok"
    except Exception as e:
        checks["s3"] = f"error: {e}"
    # Torch
    try:
        checks["torch"] = "ok"
        checks["cuda"] = "available" if torch.cuda.is_available() else "not available"
    except Exception as e:
        checks["torch"] = f"error: {e}"

    all_ok = all("ok" in str(v) or "available" in str(v) for v in checks.values())
    return {"status": "ready" if all_ok else "not ready", "checks": checks, "timestamp": datetime.utcnow().isoformat()}
