# backend/services/search_service.py
"""
Search service with Qdrant integration
"""

import numpy as np
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import logging
import time
from functools import lru_cache

from core.config import get_settings
from core.embeddings import get_embedder
from core.cache import get_cache_manager

logger = logging.getLogger(__name__)


class SearchService:
    """Production search service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedder = get_embedder()
        self.cache = get_cache_manager()
        self.qdrant = self._get_qdrant_client()
    
    def _get_qdrant_client(self) -> QdrantClient:
        """Get Qdrant client"""
        return QdrantClient(
            host=self.settings.QDRANT_HOST,
            port=self.settings.QDRANT_PORT
        )
    
    async def search(
        self,
        query: str,
        modality: str = "text",
        top_k: int = 100,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Perform multimodal search
        
        Args:
            query: Search query (text or URL for image/audio/video)
            modality: Query modality (text, image, audio, video)
            top_k: Number of results
            filters: Optional metadata filters
        
        Returns:
            Search results with metadata
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self.cache._make_key(
            "search",
            {"query": query, "modality": modality, "top_k": top_k, "filters": filters}
        )
        
        cached = self.cache.get(cache_key)
        if cached:
            cached["cache_hit"] = True
            cached["latency_ms"] = (time.time() - start_time) * 1000
            logger.info(f"✓ Cache hit for query: {query[:50]}")
            return cached
        
        # Generate query embedding
        embed_start = time.time()
        
        if modality == "text":
            query_vec = self.embedder.embed_text([query])[0]
        elif modality == "image":
            # Download image from URL and embed
            from core.storage import download_temp_file
            temp_path = download_temp_file(query)
            query_vec = self.embedder.embed_images([temp_path])[0]
        elif modality == "audio":
            from core.storage import download_temp_file
            temp_path = download_temp_file(query)
            query_vec = self.embedder.embed_audio([temp_path])[0]
        elif modality == "video":
            from core.storage import download_temp_file
            temp_path = download_temp_file(query)
            query_vec = self.embedder.embed_videos([temp_path])[0]
        else:
            raise ValueError(f"Unknown modality: {modality}")
        
        embed_time = (time.time() - embed_start) * 1000
        
        # Build filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)
        
        # Search Qdrant
        search_start = time.time()
        
        results = self.qdrant.search(
            collection_name=self.settings.QDRANT_COLLECTION,
            query_vector=query_vec.tolist(),
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        search_time = (time.time() - search_start) * 1000
        
        # Format results
        formatted_results = []
        for hit in results:
            formatted_results.append({
                "id": hit.id,
                "score": hit.score,
                "media_type": hit.payload.get("media_type"),
                "thumbnail_url": hit.payload.get("thumbnail_url"),
                "preview_url": hit.payload.get("preview_url"),
                "metadata": hit.payload
            })
        
        response = {
            "results": formatted_results,
            "total": len(formatted_results),
            "query": query,
            "modality": modality,
            "cache_hit": False,
            "latency_ms": (time.time() - start_time) * 1000,
            "metrics": {
                "embedding_ms": embed_time,
                "search_ms": search_time
            }
        }
        
        # Cache results
        self.cache.set(cache_key, response)
        
        logger.info(
            f"✓ Search completed: {query[:50]}... | "
            f"Results: {len(formatted_results)} | "
            f"Latency: {response['latency_ms']:.2f}ms"
        )
        
        return response


@lru_cache()
def get_search_service() -> SearchService:
    """Get cached search service instance"""
    return SearchService()