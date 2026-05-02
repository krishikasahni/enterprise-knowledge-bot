from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from services.auth import require_admin, User
from services import ingestion

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


class UploadResponse(BaseModel):
    message: str
    chunks: int
    source: str


class UrlIngestRequest(BaseModel):
    url: str


class SqlIngestRequest(BaseModel):
    connection_string: str
    query: str
    label: str


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
):
    content_type = file.content_type or ""
    filename = file.filename or "unknown"

    file_bytes = await file.read()

    if "pdf" in content_type or filename.endswith(".pdf"):
        chunks = ingestion.ingest_pdf(file_bytes, filename)
    elif "wordprocessingml" in content_type or filename.endswith(".docx"):
        chunks = ingestion.ingest_docx(file_bytes, filename)
    else:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type}. Upload PDF or DOCX.",
        )

    return UploadResponse(message="File ingested successfully", chunks=chunks, source=filename)


@router.post("/url", response_model=UploadResponse)
async def upload_url(
    req: UrlIngestRequest,
    admin: User = Depends(require_admin),
):
    try:
        chunks = ingestion.ingest_url(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
    return UploadResponse(message="URL ingested successfully", chunks=chunks, source=req.url)


@router.post("/sql", response_model=UploadResponse)
async def upload_sql(
    req: SqlIngestRequest,
    admin: User = Depends(require_admin),
):
    try:
        chunks = ingestion.ingest_sql(req.connection_string, req.query, req.label)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL ingestion failed: {e}")
    return UploadResponse(message="SQL data ingested successfully", chunks=chunks, source=req.label)
