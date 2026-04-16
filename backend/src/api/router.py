import os
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.rag.document_processor import extract_text, chunk_text
from src.rag.embeddings import embed_chunks
from src.rag.vector_store import create_collection_if_not_exists, store_chunks

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024

router = APIRouter(prefix="/upload", tags=["upload"])


def validate_file_size(content: bytes) -> None:
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")


def validate_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}",
        )
    return ext.lower()


@router.post("")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    validate_file_size(content)
    ext = validate_file_extension(file.filename)
    document_id = str(uuid.uuid4())

    try:
        text = extract_text(content, ext)
        chunks = chunk_text(
            text, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )
        create_collection_if_not_exists()
        embeddings = embed_chunks(chunks)
        store_chunks(chunks, embeddings, document_id, file.filename)

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "document_id": document_id,
                "filename": file.filename,
                "chunk_count": len(chunks),
                "message": "Document processed and stored successfully",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "upload_failed",
                "document_id": document_id,
                "filename": file.filename,
                "error": str(e),
            },
        )
