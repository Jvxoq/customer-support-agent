from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SupportTicket(SQLModel, table=True):
    __tablename__ = "customer-support-agent"
    __table_args__ = {"quote": True}

    ticket_id: str = Field(primary_key=True)
    user_query: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str


class Document(SQLModel, table=True):
    __tablename__ = "customer-support-document"
    __table_args__ = {"quote": True}

    document_id: str = Field(primary_key=True)
    filename: str
    file_size: int
    chunk_count: int
    status: str
    uploaded_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
