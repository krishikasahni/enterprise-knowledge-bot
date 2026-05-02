from typing import List, Tuple
from langchain.schema import Document
from db.vector_store import get_vectorstore


def retrieve(query: str, k: int = 5) -> List[Tuple[Document, float]]:
    """Return top-k documents with relevance scores."""
    vs = get_vectorstore()
    results = vs.similarity_search_with_relevance_scores(query, k=k)
    # Filter low-relevance chunks
    return [(doc, score) for doc, score in results if score > 0.3]


def retrieve_docs(query: str, k: int = 5) -> List[Document]:
    return [doc for doc, _ in retrieve(query, k)]
