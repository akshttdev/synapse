# backend/core/qdrant_client.py
"""
Qdrant wrapper for Qdrant Cloud (http URL + API key).
Using qdrant-client with cloud URL / API key.
"""
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from typing import List, Dict, Optional
import numpy as np
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_qdrant_client(url: Optional[str] = None, api_key: Optional[str] = None) -> QdrantClient:
    url = url or settings.QDRANT_URL
    api_key = api_key or settings.QDRANT_API_KEY
    if not url:
        raise ValueError("QDRANT_URL not set")
    kwargs = {"url": url}
    if api_key:
        kwargs["api_key"] = api_key
    client = QdrantClient(**kwargs)
    return client


class QdrantWrapper:
    def __init__(self, client: QdrantClient, collection: str):
        self.client = client
        self.collection = collection

    def search(self, query_vector, limit: int = 100, score_threshold: float = 0.0, query_filter=None) -> List[Dict]:
        vec = np.asarray(query_vector).tolist()
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=limit,
            with_payload=True,
            with_vector=False,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        results = []
        for h in hits:
            results.append({
                "id": str(h.id),
                "score": float(h.score) if hasattr(h, "score") else 0.0,
                "payload": dict(h.payload or {}),
            })
        return results

    def get_collection_info(self):
        try:
            info = self.client.get_collection(self.collection)
            return info
        except Exception as e:
            logger.warning(f"get_collection_info failed: {e}")
            return {}
