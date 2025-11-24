# backend/api/routes/health.py
"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check - verify all dependencies
    """
    checks = {}
    
    # Check Redis
    try:
        from core.cache import get_cache_manager
        cache = get_cache_manager()
        cache.redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    
    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        import os
        client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", "6333"))
        )
        client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {e}"
    
    # Check GPU
    try:
        import torch
        checks["gpu"] = "available" if torch.cuda.is_available() else "not available"
        if torch.cuda.is_available():
            checks["gpu_count"] = torch.cuda.device_count()
            checks["gpu_name"] = torch.cuda.get_device_name(0)
    except Exception as e:
        checks["gpu"] = f"error: {e}"
    
    all_ok = all(v == "ok" or "available" in str(v) for v in checks.values())
    
    return {
        "status": "ready" if all_ok else "not ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live")
async def liveness_check():
    """Liveness check"""
    return {"status": "alive"}