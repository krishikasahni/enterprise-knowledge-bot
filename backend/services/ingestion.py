import io
import re
from typing import List

from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sqlalchemy import create_engine, text

from db.vector_store import get_vectorstore, reset_vectorstore

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _add_to_store(docs: List[Document], source_label: str):
    vs = get_vectorstore()
    for doc in docs:
        doc.metadata["source"] = source_label
    vs.add_documents(docs)
    reset_vectorstore()


# ── PDF ────────────────────────────────────────────────────────────────────────

def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    reader = PdfReader(io.BytesIO(file_bytes))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{"type": "pdf", "filename": filename}],
    )
    _add_to_store(chunks, filename)
    return len(chunks)


# ── DOCX ───────────────────────────────────────────────────────────────────────

def ingest_docx(file_bytes: bytes, filename: str) -> int:
    doc = DocxDocument(io.BytesIO(file_bytes))
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{"type": "docx", "filename": filename}],
    )
    _add_to_store(chunks, filename)
    return len(chunks)


# ── URL / Wiki ─────────────────────────────────────────────────────────────────

def ingest_url(url: str) -> int:
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav / footer noise
    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks = splitter.create_documents(
        [text],
        metadatas=[{"type": "url", "url": url}],
    )
    _add_to_store(chunks, url)
    return len(chunks)


# ── SQL ────────────────────────────────────────────────────────────────────────

def ingest_sql(connection_string: str, query: str, label: str) -> int:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())

    lines = ["\t".join(columns)]
    for row in rows:
        lines.append("\t".join(str(v) for v in row))
    full_text = "\n".join(lines)

    chunks = splitter.create_documents(
        [full_text],
        metadatas=[{"type": "sql", "label": label, "query": query}],
    )
    _add_to_store(chunks, label)
    return len(chunks)
