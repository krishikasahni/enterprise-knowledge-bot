from typing import List, Tuple, Dict
from db.vector_store import similarity_search


def retrieve(query: str, k: int = 5) -> List[Tuple[Dict, float]]:
    return similarity_search(query, k=k)
