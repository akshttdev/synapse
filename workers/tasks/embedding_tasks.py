# workers/tasks/embedding_tasks.py
"""
GPU-ENABLED embedding tasks using ImageBind
"""

import os
import logging
from pathlib import Path
import numpy as np
from celery_app import app
from typing import Dict
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from core.embeddings import get_embedder
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def qdrant_client():
    """Get Qdrant client"""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port)


@app.task(name="workers.tasks.embedding_tasks.embed_media_task", bind=True)
def embed_media_task(
    self,
    media_id: str,
    local_path: str,
    media_type: str,
    upload_result: Dict
):
    """
    Generate embedding using ImageBind (GPU)
    Save float32 embedding to disk
    Optionally upload to Qdrant
    """
    try:
        local_path = Path(local_path)
        logger.info(f"🚀 Embedding {media_id} ({media_type}) using GPU")
        
        # Get GPU embedder
        embedder = get_embedder()
        
        # Generate embedding based on media type
        if media_type == "image":
            vec = embedder.embed_single(str(local_path), "image")
        elif media_type == "audio":
            vec = embedder.embed_single(str(local_path), "audio")
        elif media_type == "video":
            vec = embedder.embed_single(str(local_path), "video")
        else:
            raise ValueError(f"Unknown media_type: {media_type}")
        
        # Verify embedding
        assert vec.shape == (1024,), f"Invalid embedding shape: {vec.shape}"
        assert vec.dtype == np.float32, f"Invalid dtype: {vec.dtype}"
        
        # Save float32 embedding to disk
        embeddings_dir = Path(os.getenv("EMBEDDINGS_DIR", "data/embeddings"))
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        out_file = embeddings_dir / f"{media_id}.npy"
        np.save(out_file, vec)
        
        logger.info(f"✓ Saved embedding to {out_file}")
        
        # Optional: Upload directly to Qdrant (uncompressed)
        if os.getenv("UPLOAD_DIRECT_TO_QDRANT", "false").lower() in ("1", "true", "yes"):
            client = qdrant_client()
            
            point = PointStruct(
                id=media_id,
                vector=vec.tolist(),
                payload={
                    "media_id": media_id,
                    "media_type": media_type,
                    "thumbnail_url": upload_result.get("thumbnail_url"),
                    "preview_url": upload_result.get("preview_url"),
                    "storage": upload_result.get("storage", "r2")
                }
            )
            
            client.upsert(
                collection_name=os.getenv("QDRANT_COLLECTION", "media"),
                points=[point]
            )
            
            logger.info(f"✓ Uploaded to Qdrant: {media_id}")
        
        # Cleanup local file
        try:
            if local_path.exists():
                local_path.unlink()
                # Remove temp directory if empty
                parent = local_path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                logger.info(f"✓ Cleaned up {local_path}")
        except Exception as e:
            logger.warning(f"Cleanup failed for {local_path}: {e}")
        
        return {
            "status": "ok",
            "media_id": media_id,
            "embedding_file": str(out_file),
            "embedding_shape": vec.shape,
            "embedding_norm": float(np.linalg.norm(vec))
        }
    
    except Exception as exc:
        logger.exception(f"❌ Embedding failed for {media_id}: {exc}")
        raise self.retry(exc=exc, countdown=10, max_retries=3)