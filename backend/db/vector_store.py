"""
Pure Python + NumPy vector store.
Persists embeddings to a JSON file — no external DB needed.
"""
import json
import os
import traceback
import numpy as np
from typing import List, Tuple, Dict, Any
from openai import OpenAI
from config import get_settings

settings = get_settings()
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
STORE_PATH = os.path.join(settings.chroma_persist_dir, "vectors.json")

_openai_client = None
_store: List[Dict[str, Any]] = []
_loaded = False


def _get_openai():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


def _embed(texts: List[str]) -> List[List[float]]:
    resp = _get_openai().embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in resp.data]


def _load():
    global _store, _loaded
    if _loaded:
        return
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "r") as f:
                _store = json.load(f)
        except Exception:
            _store = []
    _loaded = True


def _save():
    try:
        with open(STORE_PATH, "w") as f:
            json.dump(_store, f)
    except Exception as e:
        print(f"Warning: could not save vector store: {e}")


def add_documents(texts: List[str], metadatas: List[Dict]) -> int:
    global _loaded
    _load()
    if not texts:
        return 0
    # Embed in batches of 20
    all_embeddings = []
    for i in range(0, len(texts), 20):
        batch = texts[i:i+20]
        all_embeddings.extend(_embed(batch))
    
    for text, meta, emb in zip(texts, metadatas, all_embeddings):
        _store.append({"text": text, "metadata": meta, "embedding": emb})
    _save()
    return len(texts)


def similarity_search(query: str, k: int = 5) -> List[Tuple[Dict, float]]:
    _load()
    if not _store:
        return []
    try:
        q_emb = np.array(_embed([query])[0])
        results = []
        for item in _store:
            emb = np.array(item["embedding"])
            norm = np.linalg.norm(q_emb) * np.linalg.norm(emb)
            score = float(np.dot(q_emb, emb) / norm) if norm > 0 else 0.0
            results.append((item, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [(item, score) for item, score in results[:k] if score > 0.2]
    except Exception as e:
        traceback.print_exc()
        return []
