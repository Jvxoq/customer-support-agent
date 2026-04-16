import io
import os
from typing import List

import markdown
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text_from_md(file_bytes: bytes) -> str:
    return markdown.markdown(file_bytes.decode("utf-8"))


EXTRACTORS = {
    ".pdf": extract_text_from_pdf,
    ".doc": extract_text_from_docx,
    ".docx": extract_text_from_docx,
    ".md": extract_text_from_md,
}


def extract_text(file_bytes: bytes, extension: str) -> str:
    extractor = EXTRACTORS.get(extension.lower())
    if not extractor:
        raise ValueError(f"Unsupported file type: {extension}")
    return extractor(file_bytes)


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks
