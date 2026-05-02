import io
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from sqlalchemy import create_engine, text

from db.vector_store import add_documents

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80


def _chunk_text(text: str) -> List[str]:
    # Split into sentences/paragraphs first
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    paragraphs = text.split('\n\n')
    
    chunks = []
    current = []
    length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if length + len(para) > CHUNK_SIZE and current:
            chunks.append('\n\n'.join(current))
            current = current[-1:]  # keep last para for overlap
            length = len(current[0]) if current else 0
        current.append(para)
        length += len(para)
    
    if current:
        chunks.append('\n\n'.join(current))
    
    return [c for c in chunks if len(c.strip()) > 30]


def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        full_text = '\n\n'.join(pages)
        if not full_text.strip():
            raise ValueError("No text could be extracted from this PDF. It may be scanned/image-based.")
        chunks = _chunk_text(full_text)
        meta = [{"source": filename, "type": "pdf"} for _ in chunks]
        return add_documents(chunks, meta)
    except Exception as e:
        raise RuntimeError(f"PDF ingestion error: {str(e)}")


def ingest_docx(file_bytes: bytes, filename: str) -> int:
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = '\n\n'.join(paragraphs)
        if not full_text.strip():
            raise ValueError("No text found in this DOCX file.")
        chunks = _chunk_text(full_text)
        meta = [{"source": filename, "type": "docx"} for _ in chunks]
        return add_documents(chunks, meta)
    except Exception as e:
        raise RuntimeError(f"DOCX ingestion error: {str(e)}")


def ingest_url(url: str) -> int:
    try:
        session = requests.Session()
        resp = session.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (compatible; KnowledgeBot/1.0)"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        if not text:
            raise ValueError("No readable text found at this URL.")
        chunks = _chunk_text(text)
        meta = [{"source": url, "type": "url"} for _ in chunks]
        return add_documents(chunks, meta)
    except Exception as e:
        raise RuntimeError(f"URL ingestion error: {str(e)}")


def ingest_sql(connection_string: str, query: str, label: str) -> int:
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())
        lines = ["\t".join(columns)]
        for row in rows:
            lines.append("\t".join(str(v) for v in row))
        full_text = "\n".join(lines)
        chunks = _chunk_text(full_text)
        meta = [{"source": label, "type": "sql"} for _ in chunks]
        return add_documents(chunks, meta)
    except Exception as e:
        raise RuntimeError(f"SQL ingestion error: {str(e)}")
