import chromadb
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from config import get_settings

settings = get_settings()

_client = None
_vectorstore = None


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.Client(
            chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.chroma_persist_dir,
                anonymized_telemetry=False,
            )
        )
    return _client


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
        )
        _vectorstore = Chroma(
            client=get_chroma_client(),
            collection_name="knowledge_base",
            embedding_function=embeddings,
        )
    return _vectorstore


def reset_vectorstore():
    global _vectorstore
    _vectorstore = None
