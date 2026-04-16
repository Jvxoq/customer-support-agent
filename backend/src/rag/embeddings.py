from typing import List

from sentence_transformers import SentenceTransformer

from src.config.settings import get_settings

settings = get_settings()

_model = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    return model.encode(chunks, show_progress_bar=True).tolist()


def embed_query(query: str) -> List[float]:
    model = get_embedding_model()
    return model.encode([query], show_progress_bar=False).tolist()[0]
