import io
import re
from typing import List
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from sqlalchemy import create_engine, text
from db.vector_store import add_documents

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def _chunk_text(text: str) -> List[str]:
    words = text.split()
    chunks, current = [], []
    length = 0
    for word in words:
        current.append(word)
        length += len(word) + 1
        if length >= CHUNK_SIZE:
            chunks.append(" ".join(current))
            current = current[-CHUNK_OVERLAP:]
            length = sum(len(w) + 1 for w in current)
    if current:
        chunks.append(" ".join(current))
    return [c for c in chunks if len(c.strip()) > 50]


def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    chunks = _chunk_text(text)
    meta = [{"source": filename, "type": "pdf"} for _ in chunks]
    return add_documents(chunks, meta)


def ingest_docx(file_bytes: bytes, filename: str) -> int:
    doc = DocxDocument(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    chunks = _chunk_text(text)
    meta = [{"source": filename, "type": "docx"} for _ in chunks]
    return add_documents(chunks, meta)


def ingest_url(url: str) -> int:
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()
    text = re.sub(r"\n{3,}", "\n\n", soup.get_text(separator="\n")).strip()
    chunks = _chunk_text(text)
    meta = [{"source": url, "type": "url"} for _ in chunks]
    return add_documents(chunks, meta)


def ingest_sql(connection_string: str, query: str, label: str) -> int:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())
    lines = ["\t".join(columns)] + ["\t".join(str(v) for v in row) for row in rows]
    chunks = _chunk_text("\n".join(lines))
    meta = [{"source": label, "type": "sql"} for _ in chunks]
    return add_documents(chunks, meta)
