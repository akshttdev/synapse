# backend/services/search_service.py
import time
import logging
from typing import Optional, Dict, List
import numpy as np
from functools import lru_cache

from core.config import get_settings
from core.embeddings import get_embedder
from core.cache import get_cache_manager
from core.qdrant_client import get_qdrant_client, QdrantWrapper
from qdrant_client.http.models import FieldCondition, MatchValue, Filter

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.settings = get_settings()
        self.embedder = get_embedder(device=self.settings.MODEL_DEVICE, batch_size=self.settings.BATCH_SIZE)
        self.cache = get_cache_manager()
        qclient = get_qdrant_client(self.settings.QDRANT_HOST, self.settings.QDRANT_PORT)
        self.qdrant = QdrantWrapper(qclient, self.settings.QDRANT_COLLECTION)

    async def search(
        self,
        query: str,
        modality: str = "text",
        top_k: int = 50,
        filters: Optional[Dict] = None
    ) -> Dict:
        start = time.time()

        cache_key = self.cache._make_key("search", {"q": query, "modality": modality, "top_k": top_k, "filters": filters})
        cached = self.cache.get(cache_key)
        if cached:
            cached["cache_hit"] = True
            cached["latency_ms"] = (time.time() - start) * 1000
            return cached

        # Build embedding
        emb_start = time.time()
        if modality == "text":
            vec = self.embedder.embed_text([query])[0]
        elif modality in ("image", "audio", "video"):
            # query should be a URL or local path
            from core.storage import download_temp_file
            temp_path = download_temp_file(query)
            vec = self.embedder.embed_single(str(temp_path), modality)
            try:
                temp_path.unlink()
                temp_path.parent.rmdir()
            except Exception:
                pass
        else:
            raise ValueError("Unknown modality")

        emb_ms = (time.time() - emb_start) * 1000

        # qdrant filter
        qdr_filter = None
        if filters:
            conds = []
            for k, v in filters.items():
                conds.append(FieldCondition(key=k, match=MatchValue(value=v)))
            if conds:
                qdr_filter = Filter(must=conds)

        # Search
        search_start = time.time()
        hits = self.qdrant.search(query_vector=vec, limit=top_k, score_threshold=0.0, query_filter=qdr_filter)
        search_ms = (time.time() - search_start) * 1000

        results = []
        for r in hits:
            payload = r.get("payload", {})
            results.append({
                "id": r.get("id"),
                "score": r.get("score"),
                "media_type": payload.get("media_type"),
                "thumbnail_url": payload.get("thumbnail_url"),
                "preview_url": payload.get("preview_url"),
                "metadata": payload
            })

        resp = {
            "results": results,
            "total": len(results),
            "query": query,
            "modality": modality,
            "cache_hit": False,
            "latency_ms": (time.time() - start) * 1000,
            "metrics": {
                "embedding_ms": round(emb_ms, 2),
                "search_ms": round(search_ms, 2)
            }
        }

        # cache
        try:
            self.cache.set(cache_key, resp)
        except Exception:
            logger.debug("cache set failed")

        return resp


@lru_cache()
def get_search_service() -> SearchService:
    return SearchService()
