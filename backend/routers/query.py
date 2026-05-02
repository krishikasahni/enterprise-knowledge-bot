from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from services.auth import get_current_user, User
from services.retriever import retrieve
from services.llm import answer, answer_stream

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    stream: bool = False
    top_k: int = 5


class SourceMeta(BaseModel):
    source: str
    score: float
    preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceMeta]


@router.post("", response_model=QueryResponse)
async def query(req: QueryRequest, user: User = Depends(get_current_user)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    results = retrieve(req.question, k=req.top_k)
    if not results:
        return QueryResponse(
            answer="I don't have any relevant documents in the knowledge base yet. Please ask an admin to upload some documents first.",
            sources=[],
        )

    docs = [item for item, _ in results]
    sources = [
        SourceMeta(
            source=item["metadata"].get("source", "unknown"),
            score=round(score, 3),
            preview=item["text"][:200],
        )
        for item, score in results
    ]

    if req.stream:
        async def event_stream():
            async for chunk in answer_stream(req.question, docs):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    response_text = await answer(req.question, docs)
    return QueryResponse(answer=response_text, sources=sources)
