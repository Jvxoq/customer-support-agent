from typing import List

from src.rag.embeddings import embed_query
from src.rag.vector_store import search_similar_chunks


def retrieve_context(query: str, top_k: int = 5) -> List[dict]:
    query_embedding = embed_query(query)
    return search_similar_chunks(query_embedding, limit=top_k)


def format_context(context: List[dict]) -> str:
    formatted_parts = []
    for i, item in enumerate(context, 1):
        source = f"[{item['filename']}]"
        formatted_parts.append(f"{source}\n{item['text']}")
    return "\n\n".join(formatted_parts)
