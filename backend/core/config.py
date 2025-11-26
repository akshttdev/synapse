from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Synapse"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Qdrant Cloud
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "synapse_vectors"

    # Disable legacy vars safely
    QDRANT_HOST: str | None = None
    QDRANT_PORT: int | None = None

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = ""
    S3_PRESIGNED_EXPIRATION: int = 3600

    # Model
    MODEL_DEVICE: str = "cpu"
    BATCH_SIZE: int = 32

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings():
    return Settings()
