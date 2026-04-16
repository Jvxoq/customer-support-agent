import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.db.database import save_document
from src.rag.document_processor import extract_text, chunk_text
from src.rag.embeddings import embed_chunks
from src.rag.vector_store import create_collection_if_not_exists, store_chunks
from src.system.logger import logger


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Application started")
        yield
        logger.info("Application shutting down")

    app = FastAPI(
        title="Customer Support Agent API",
        version="1.0.0",
        lifespan=lifespan,
    )

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )

    ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".md"}
    MAX_FILE_SIZE = 10 * 1024 * 1024

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

    @app.post("/api/v1/upload")
    @limiter.limit("10/minute")
    async def upload_document(request: Request, file: UploadFile = File(...)):
        document_id = str(uuid.uuid4())
        logger.info(
            f"Upload request received | file={file.filename} | document_id={document_id}"
        )

        content = await file.read()
        validate_file_size(content)
        ext = validate_file_extension(file.filename)

        try:
            logger.info(f"Extracting text | document_id={document_id}")
            text = extract_text(content, ext)

            logger.info(
                f"Chunking text | document_id={document_id} | chunk_size={settings.chunk_size}"
            )
            chunks = chunk_text(
                text,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )

            logger.info(f"Initializing Qdrant collection | document_id={document_id}")
            create_collection_if_not_exists()

            logger.info(
                f"Embedding chunks | document_id={document_id} | chunk_count={len(chunks)}"
            )
            embeddings = embed_chunks(chunks)

            logger.info(f"Storing embeddings in Qdrant | document_id={document_id}")
            store_chunks(chunks, embeddings, document_id, file.filename)

            logger.info(f"Saving document metadata to DB | document_id={document_id}")
            save_document(
                document_id=document_id,
                filename=file.filename,
                file_size=len(content),
                chunk_count=len(chunks),
                status="uploaded",
            )

            logger.info(f"Upload completed successfully | document_id={document_id}")
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
            logger.error(f"Upload failed | document_id={document_id} | error={str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "upload_failed",
                    "document_id": document_id,
                    "filename": file.filename,
                    "error": str(e),
                },
            )

    @app.get("/")
    async def root(request: Request):
        return {
            "name": "Customer Support Agent",
            "version": "1.0.0",
            "status": "healthy",
        }

    @app.get("/health")
    async def health_check(request: Request) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
        }

    return app


app = create_app()
