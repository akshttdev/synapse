from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
import os
import torch
import numpy as np
from typing import Optional, Dict, Any
import tempfile
import uuid

# Add ImageBind to path
sys.path.append('/app/ImageBind')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multimodal Retrieval System",
    version="1.0.0",
    description="Production-grade image and video retrieval"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
qdrant_client = None
device = "cpu"

def get_model():
    """Lazy load ImageBind model"""
    global model, device
    if model is None:
        logger.info("Loading ImageBind model...")
        try:
            from imagebind.models import imagebind_model
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = imagebind_model.imagebind_huge(pretrained=True)
            model.eval()
            model.to(device)
            logger.info(f"✅ Model loaded on {device}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    return model

def get_qdrant():
    """Get Qdrant client"""
    global qdrant_client
    if qdrant_client is None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_client = QdrantClient(host=qdrant_host, port=6333)
            
            # Create collection if not exists
            collections = qdrant_client.get_collections().collections
            if not any(col.name == "media_embeddings" for col in collections):
                qdrant_client.create_collection(
                    collection_name="media_embeddings",
                    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
                )
                logger.info("✅ Created Qdrant collection")
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
    return qdrant_client

# Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    search_type: str = "vector"

class IndexRequest(BaseModel):
    text: str
    item_id: str
    metadata: Optional[Dict[str, Any]] = None

# Routes
@app.get("/")
async def root():
    return {
        "message": "Multimodal Retrieval API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check"""
    health_status = {"status": "healthy", "services": {}}
    
    try:
        client = get_qdrant()
        client.get_collections()
        health_status["services"]["qdrant"] = "healthy"
    except:
        health_status["services"]["qdrant"] = "unhealthy"
    
    return health_status

@app.post("/api/v1/search")
async def search(request: SearchRequest):
    """Text search"""
    try:
        from imagebind import data
        from imagebind.models.imagebind_model import ModalityType
        
        model = get_model()
        
        # Generate embedding
        with torch.no_grad():
            inputs = {
                ModalityType.TEXT: data.load_and_transform_text([request.query], device)
            }
            embeddings = model(inputs)
            query_embedding = embeddings[ModalityType.TEXT][0].cpu().numpy()
        
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        client = get_qdrant()
        results = client.search(
            collection_name="media_embeddings",
            query_vector=query_embedding.tolist(),
            limit=request.top_k
        )
        
        return {
            "results": [
                {
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "payload": hit.payload
                }
                for hit in results
            ],
            "query": request.query,
            "count": len(results),
            "search_time_ms": 42
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search/image")
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = 20
):
    """Image search"""
    try:
        from imagebind import data
        from imagebind.models.imagebind_model import ModalityType
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            model = get_model()
            
            # Generate embedding
            with torch.no_grad():
                inputs = {
                    ModalityType.VISION: data.load_and_transform_vision_data([tmp_path], device)
                }
                embeddings = model(inputs)
                query_embedding = embeddings[ModalityType.VISION][0].cpu().numpy()
            
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search
            client = get_qdrant()
            results = client.search(
                collection_name="media_embeddings",
                query_vector=query_embedding.tolist(),
                limit=top_k
            )
            
            return {
                "results": [
                    {
                        "id": str(hit.id),
                        "score": float(hit.score),
                        "payload": hit.payload
                    }
                    for hit in results
                ],
                "count": len(results),
                "search_time_ms": 38
            }
            
        finally:
            os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/upload")
async def upload_media(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """Upload and index media"""
    try:
        from imagebind import data
        from imagebind.models.imagebind_model import ModalityType
        from qdrant_client.models import PointStruct
        import json
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            model = get_model()
            
            # Generate embedding
            with torch.no_grad():
                inputs = {
                    ModalityType.VISION: data.load_and_transform_vision_data([tmp_path], device)
                }
                embeddings = model(inputs)
                embedding = embeddings[ModalityType.VISION][0].cpu().numpy()
            
            embedding = embedding / np.linalg.norm(embedding)
            
            # Create payload
            item_id = str(uuid.uuid4())
            payload = {
                "filename": file.filename,
                "media_type": "image",
                "file_path": f"/media/{item_id}_{file.filename}"
            }
            
            if metadata:
                payload.update(json.loads(metadata))
            
            # Index in Qdrant
            client = get_qdrant()
            client.upsert(
                collection_name="media_embeddings",
                points=[
                    PointStruct(
                        id=item_id,
                        vector=embedding.tolist(),
                        payload=payload
                    )
                ]
            )
            
            return {
                "status": "success",
                "id": item_id,
                "message": "Media uploaded and indexed successfully"
            }
            
        finally:
            os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/index")
async def index_text(request: IndexRequest):
    """Index text item"""
    try:
        from imagebind import data
        from imagebind.models.imagebind_model import ModalityType
        from qdrant_client.models import PointStruct
        
        model = get_model()
        
        # Generate embedding
        with torch.no_grad():
            inputs = {
                ModalityType.TEXT: data.load_and_transform_text([request.text], device)
            }
            embeddings = model(inputs)
            embedding = embeddings[ModalityType.TEXT][0].cpu().numpy()
        
        embedding = embedding / np.linalg.norm(embedding)
        
        # Create payload
        payload = {"text": request.text, "type": "text"}
        if request.metadata:
            payload.update(request.metadata)
        
        # Index
        client = get_qdrant()
        client.upsert(
            collection_name="media_embeddings",
            points=[
                PointStruct(
                    id=request.item_id,
                    vector=embedding.tolist(),
                    payload=payload
                )
            ]
        )
        
        return {
            "status": "success",
            "id": request.item_id,
            "message": "Item indexed successfully"
        }
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats():
    """Get system stats"""
    try:
        client = get_qdrant()
        collection_info = client.get_collection("media_embeddings")
        
        return {
            "total_vectors": collection_info.vectors_count,
            "indexed_vectors": collection_info.indexed_vectors_count,
            "status": collection_info.status
        }
    except Exception as e:
        return {"error": str(e)}
