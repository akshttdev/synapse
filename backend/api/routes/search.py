# backend/api/routes/search.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging

from services.search_service import get_search_service, SearchService

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    modality: str = Field(default="text")
    top_k: int = Field(default=50, ge=1, le=1000)
    filters: Optional[Dict] = None


class SearchResponse(BaseModel):
    results: List[Dict]
    total: int
    query: str
    latency_ms: float
    metrics: Optional[Dict] = None


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest, search_service: SearchService = Depends(get_search_service)):
    try:
        res = await search_service.search(
            query=request.query,
            modality=request.modality,
            top_k=request.top_k,
            filters=request.filters
        )
        return res
    except Exception as e:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail=str(e))
