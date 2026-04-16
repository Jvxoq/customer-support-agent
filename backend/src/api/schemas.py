from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class RetrievedContext(BaseModel):
    text: str
    document_id: str
    filename: str
    score: float


class QueryResponse(BaseModel):
    status: str
    query: str
    context: List[RetrievedContext]
    formatted_context: str
