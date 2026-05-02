import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import get_settings

settings = get_settings()

_client = None
_vectorstore = None


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-3-small",
        )
        _vectorstore = Chroma(
            client=get_chroma_client(),
            collection_name="knowledge_base",
            embedding_function=embeddings,
        )
    return _vectorstore


def reset_vectorstore():
    """Call this after adding documents so retriever picks up new data."""
    global _vectorstore
    _vectorstore = None
