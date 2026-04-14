import os
from dotenv import load_dotenv

from sqlmodel import SQLModel, create_engine
from models import SupportTicket, Document

load_dotenv()  # Loads .env file
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
engine = create_engine(
    f"postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5432/support_db", echo=False
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


create_db_and_tables()
