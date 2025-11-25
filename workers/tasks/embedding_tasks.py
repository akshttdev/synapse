# backend/workers/tasks/embedding_tasks.py
from celery_app import app
import logging
from core.embeddings import get_embedder
from core.qdrant_client import get_qdrant_client, QdrantWrapper
import numpy as np
import os
from qdrant_client.http.models import PointStruct

logger = logging.getLogger(__name__)


def qdrant_client():
    from core.config import get_settings
    s = get_settings()
    return get_qdrant_client(s.QDRANT_URL, s.QDRANT_API_KEY)


@app.task(bind=True, name="workers.tasks.embedding_tasks.embed_media_task", max_retries=3)
def embed_media_task(self, media_id: str, local_path: str, media_type: str, upload_result: dict):
    try:
        embedder = get_embedder()
        vec = embedder.embed_single(local_path, media_type)
        vec = np.asarray(vec, dtype=np.float32)

        emb_dir = os.getenv("EMBEDDINGS_DIR", "/app/data/embeddings")
        os.makedirs(emb_dir, exist_ok=True)
        out_file = os.path.join(emb_dir, f"{media_id}.npy")
        np.save(out_file, vec)
        logger.info(f"Saved embedding {out_file}")

        # Optionally upload to Qdrant Cloud
        if os.getenv("UPLOAD_DIRECT_TO_QDRANT", "false").lower() in ("1", "true", "yes"):
            q = qdrant_client()
            wrapper = QdrantWrapper(q, os.getenv("QDRANT_COLLECTION", "media"))
            point = PointStruct(id=media_id, vector=vec.tolist(), payload={
                "media_id": media_id,
                "media_type": media_type,
                "thumbnail_url": upload_result.get("thumbnail_url"),
                "preview_url": upload_result.get("preview_url"),
                "file_key": upload_result.get("file_key"),
            })
            q.upsert(collection_name=os.getenv("QDRANT_COLLECTION", "media"), points=[point])
            logger.info(f"Uploaded to Qdrant: {media_id}")

        return {"status": "ok", "media_id": media_id, "embedding_file": out_file}
    except Exception as e:
        logger.exception("Embedding failed")
        raise self.retry(exc=e, countdown=10)
