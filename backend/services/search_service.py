import time
import logging
from typing import Optional, Dict
from functools import lru_cache

from core.config import get_settings
from core.embeddings import get_embedder
from core.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.settings = get_settings()

        self.embedder = get_embedder(
            device=self.settings.MODEL_DEVICE,
            batch_size=self.settings.BATCH_SIZE
        )

        # No cache for now
        self.cache = None

        # Qdrant Cloud client
        self.qdrant = get_qdrant_client(
            url=self.settings.QDRANT_URL,
            api_key=self.settings.QDRANT_API_KEY
        )

        self.collection = self.settings.QDRANT_COLLECTION

    async def search(
        self,
        query: str,
        modality: str = "text",
        top_k: int = 50,
        filters: Optional[Dict] = None
    ) -> Dict:

        start = time.time()

        embed_start = time.time()
        vec = self.embedder.embed_text([query])[0]
        embed_ms = (time.time() - embed_start) * 1000

        search_start = time.time()
        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=vec.tolist(),
            limit=top_k,
            with_payload=True,
        )
        search_ms = (time.time() - search_start) * 1000

        out = []
        for r in results:
            payload = r.payload or {}
            out.append({
                "id": r.id,
                "score": r.score,
                "thumbnail_url": payload.get("thumbnail_url"),
                "preview_url": payload.get("preview_url"),
                "metadata": payload,
            })

        return {
            "results": out,
            "total": len(out),
            "query": query,
            "latency_ms": (time.time() - start) * 1000,
            "metrics": {
                "embedding_ms": round(embed_ms, 2),
                "search_ms": round(search_ms, 2)
            }
        }


@lru_cache()
def get_search_service() -> SearchService:
    return SearchService()
