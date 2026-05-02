from typing import List, Dict, AsyncIterator
from openai import AsyncOpenAI
from config import get_settings

settings = get_settings()
_client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _build_context(docs: List[Dict]) -> str:
    parts = []
    for i, item in enumerate(docs, 1):
        src = item["metadata"].get("source", "unknown")
        parts.append(f"[Doc {i} | {src}]\n{item['text']}")
    return "\n\n---\n\n".join(parts)


SYSTEM = """You are an expert enterprise knowledge assistant.
Answer questions using ONLY the provided context documents.
If the answer is not in the context, say "I don't have enough information in the knowledge base to answer that."
Always end your answer with: Sources: [list the sources you used]"""


async def answer(question: str, docs: List[Dict]) -> str:
    context = _build_context(docs)
    resp = await get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content


async def answer_stream(question: str, docs: List[Dict]) -> AsyncIterator[str]:
    context = _build_context(docs)
    stream = await get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
