# backend/api/routes/search.py
"""
Search endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging

from services.search_service import SearchService, get_search_service

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    modality: str = Field(default="text", pattern="^(text|image|audio|video)$")
    top_k: int = Field(default=100, ge=1, le=1000)
    filters: Optional[Dict] = None


class SearchResponse(BaseModel):
    results: List[Dict]
    total: int
    query: str
    latency_ms: float


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Multimodal semantic search
    
    - **query**: Search query (text, image URL, audio URL, video URL)
    - **modality**: Query type (text, image, audio, video)
    - **top_k**: Number of results (max 1000)
    - **filters**: Optional metadata filters
    """
    try:
        results = await search_service.search(
            query=request.query,
            modality=request.modality,
            top_k=request.top_k,
            filters=request.filters
        )
        return results
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))