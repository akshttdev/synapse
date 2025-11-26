from qdrant_client import QdrantClient


def get_qdrant_client(url: str, api_key: str) -> QdrantClient:
    """
    Always use Qdrant Cloud over HTTPS.
    No host/port. No timeout. No wrappers.
    """
    return QdrantClient(
        url=url,
        api_key=api_key,
        timeout=30,           # Safe default built-in
    )
