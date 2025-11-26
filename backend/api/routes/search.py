from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging

from services.search_service import get_search_service, SearchService

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    modality: str = "text"
    top_k: int = 50
    filters: Optional[Dict] = None


class SearchResponse(BaseModel):
    results: List[Dict]
    total: int
    query: str
    latency_ms: float
    metrics: Optional[Dict] = None


@router.post("", response_model=SearchResponse)
async def search_api(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
):
    try:
        return await search_service.search(
            query=request.query,
            modality=request.modality,
            top_k=request.top_k,
            filters=request.filters
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
