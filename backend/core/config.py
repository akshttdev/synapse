# backend/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Synapse"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Qdrant Cloud
    QDRANT_URL: str = "https://your-qdrant-cloud-endpoint"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "media"
    EMBEDDING_DIM: int = 1024

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    S3_PRESIGNED_EXPIRATION: int = 3600

    # Model
    MODEL_DEVICE: str = "cuda:0"
    BATCH_SIZE: int = 32

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    BROKER_URL: Optional[str] = None
    RESULT_BACKEND: Optional[str] = None

    # Paths
    UPLOAD_DIR: str = "/tmp/synapse_uploads"
    EMBEDDINGS_DIR: str = "/app/data/embeddings"

    # Options
    UPLOAD_DIRECT_TO_QDRANT: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
