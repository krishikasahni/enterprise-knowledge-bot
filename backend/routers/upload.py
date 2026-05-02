from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from services.auth import require_admin, User
from services import ingestion
import traceback

router = APIRouter(prefix="/upload", tags=["upload"])


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
    try:
        filename = file.filename or "unknown"
        file_bytes = await file.read()

        if filename.lower().endswith(".pdf"):
            chunks = ingestion.ingest_pdf(file_bytes, filename)
        elif filename.lower().endswith(".docx"):
            chunks = ingestion.ingest_docx(file_bytes, filename)
        else:
            raise HTTPException(status_code=415, detail="Only PDF and DOCX files are supported.")

        return UploadResponse(message="File ingested successfully", chunks=chunks, source=filename)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {str(e)}")


@router.post("/url", response_model=UploadResponse)
async def upload_url(
    req: UrlIngestRequest,
    admin: User = Depends(require_admin),
):
    try:
        chunks = ingestion.ingest_url(req.url)
        return UploadResponse(message="URL ingested successfully", chunks=chunks, source=req.url)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")


@router.post("/sql", response_model=UploadResponse)
async def upload_sql(
    req: SqlIngestRequest,
    admin: User = Depends(require_admin),
):
    try:
        chunks = ingestion.ingest_sql(req.connection_string, req.query, req.label)
        return UploadResponse(message="SQL data ingested successfully", chunks=chunks, source=req.label)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"SQL ingestion failed: {str(e)}")
