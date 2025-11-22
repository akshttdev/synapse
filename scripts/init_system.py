#!/usr/bin/env python3
"""
Initialize the system - create collections, test connections
"""
import asyncio
import sys
sys.path.append('/app')

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import redis
import psycopg2

async def init_qdrant():
    """Initialize Qdrant collection"""
    print("🔧 Initializing Qdrant...")
    try:
        client = QdrantClient(host="qdrant", port=6333)
        
        # Create collection
        collections = client.get_collections().collections
        if not any(col.name == "media_embeddings" for col in collections):
            client.create_collection(
                collection_name="media_embeddings",
                vectors_config=VectorParams(
                    size=1024,  # ImageBind dimension
                    distance=Distance.COSINE
                )
            )
            print("✅ Created Qdrant collection")
        else:
            print("✅ Qdrant collection already exists")
    except Exception as e:
        print(f"❌ Qdrant initialization failed: {e}")

def init_redis():
    """Test Redis connection"""
    print("🔧 Testing Redis...")
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        r.set('test_key', 'test_value')
        assert r.get('test_key') == 'test_value'
        r.delete('test_key')
        print("✅ Redis is working")
    except Exception as e:
        print(f"❌ Redis test failed: {e}")

def init_postgres():
    """Initialize PostgreSQL"""
    print("🔧 Initializing PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="retrieval_db",
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id VARCHAR(36) PRIMARY KEY,
                file_path TEXT NOT NULL,
                media_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                indexed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ PostgreSQL initialized")
    except Exception as e:
        print(f"❌ PostgreSQL initialization failed: {e}")

async def main():
    print("🚀 Initializing Multimodal Retrieval System...\n")
    
    await init_qdrant()
    init_redis()
    init_postgres()
    
    print("\n✅ System initialization complete!")

if __name__ == "__main__":
    asyncio.run(main())
