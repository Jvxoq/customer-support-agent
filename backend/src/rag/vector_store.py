from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid

from src.config.settings import get_settings

settings = get_settings()

_client = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return _client


def create_collection_if_not_exists():
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if "support_docs" not in collections:
        client.create_collection(
            collection_name="support_docs",
            vectors_config=VectorParams(
                size=settings.embedding_dim, distance=Distance.COSINE
            ),
        )


def store_chunks(
    chunks: list[str], embeddings: list[list[float]], document_id: str, filename: str
):
    client = get_qdrant_client()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "document_id": document_id,
                "filename": filename,
            },
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(collection_name="support_docs", points=points)


def search_similar_chunks(query_embedding: list[float], limit: int = 5) -> list[dict]:
    client = get_qdrant_client()
    results = client.search(
        collection_name="support_docs",
        query_vector=query_embedding,
        limit=limit,
    )
    return [
        {
            "text": hit.payload["text"],
            "document_id": hit.payload["document_id"],
            "filename": hit.payload["filename"],
            "score": hit.score,
        }
        for hit in results
    ]
