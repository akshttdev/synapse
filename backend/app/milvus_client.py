# app/milvus_client.py
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)
import numpy as np
import os

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "512"))
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "synapse_audio")

_connected = False


def connect():
    global _connected
    if not _connected:
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        _connected = True


def init_collection():
    """
    Create collection if not exists: id (int64), embedding (float vector), metadata (json/string)
    """
    connect()
    if utility.has_collection(COLLECTION_NAME):
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
        FieldSchema(name="meta", dtype=DataType.VARCHAR, max_length=2048)
    ]
    schema = CollectionSchema(fields=fields, description="Synapse audio embeddings")
    coll = Collection(name=COLLECTION_NAME, schema=schema)
    # create index
    coll.create_index(field_name="embedding", params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}})
    coll.load()
    return coll


def search_vector(emb: np.ndarray, top_k=10):
    """
    emb: 1D numpy array
    returns: raw results list
    """
    connect()
    coll = Collection(COLLECTION_NAME)
    # search requires shape: [[...]]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = coll.search([emb.tolist()], "embedding", param=search_params, limit=top_k, expr=None, output_fields=["meta"])
    # parse results
    parsed = []
    for hits in results:
        for h in hits:
            parsed.append({
                "id": h.id,
                "score": float(h.distance),
                "meta": h.entity.get("meta", None)
            })
    return parsed
