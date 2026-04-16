import os
from dotenv import load_dotenv

from sqlmodel import SQLModel, create_engine, Session
from src.db.models import SupportTicket, Document

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
    echo=False,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def save_document(
    document_id: str,
    filename: str,
    file_size: int,
    chunk_count: int,
    status: str = "uploaded",
) -> Document:
    with Session(engine) as session:
        doc = Document(
            document_id=document_id,
            filename=filename,
            file_size=file_size,
            chunk_count=chunk_count,
            status=status,
        )
        session.add(doc)
        session.commit()
        return doc


def update_document(document_id: str, status: str) -> Document:
    with Session(engine) as session:
        doc = session.get(Document, document_id)
        if doc:
            doc.status = status
            session.commit()
            session.refresh(doc)
        return doc
