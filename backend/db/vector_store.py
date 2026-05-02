"""
Pure Python + NumPy vector store.
No ChromaDB, no FAISS, no Rust — just numpy dot products.
Persists to a simple JSON file.
"""
import json
import os
import numpy as np
from typing import List, Tuple, Dict, Any
from openai import OpenAI
from config import get_settings

settings = get_settings()
STORE_PATH = os.path.join(settings.chroma_persist_dir, "vectors.json")

_client = None
_store: List[Dict[str, Any]] = []   # [{text, metadata, embedding}]


def _get_openai():
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def _embed(texts: List[str]) -> List[List[float]]:
    resp = _get_openai().embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in resp.data]


def _load():
    global _store
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, "r") as f:
            _store = json.load(f)


def _save():
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(_store, f)


def add_documents(texts: List[str], metadatas: List[Dict]) -> int:
    _load()
    embeddings = _embed(texts)
    for text, meta, emb in zip(texts, metadatas, embeddings):
        _store.append({"text": text, "metadata": meta, "embedding": emb})
    _save()
    return len(texts)


def similarity_search(query: str, k: int = 5) -> List[Tuple[Dict, float]]:
    _load()
    if not _store:
        return []

    q_emb = np.array(_embed([query])[0])
    results = []
    for item in _store:
        emb = np.array(item["embedding"])
        score = float(np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb) + 1e-9))
        results.append((item, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [(item, score) for item, score in results[:k] if score > 0.3]
