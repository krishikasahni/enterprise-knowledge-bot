import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from config import get_settings

settings = get_settings()

FAISS_PATH = os.path.join(settings.chroma_persist_dir, "faiss_index")
_vectorstore = None


def get_embeddings():
    return OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key,
        model="text-embedding-3-small",
    )


def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = get_embeddings()

    if os.path.exists(FAISS_PATH):
        _vectorstore = FAISS.load_local(
            FAISS_PATH, embeddings, allow_dangerous_deserialization=True
        )
    else:
        dummy = [Document(page_content="Knowledge base initialized.", metadata={"source": "system"})]
        _vectorstore = FAISS.from_documents(dummy, embeddings)
        _save()

    return _vectorstore


def _save():
    os.makedirs(FAISS_PATH, exist_ok=True)
    if _vectorstore:
        _vectorstore.save_local(FAISS_PATH)


def reset_vectorstore():
    global _vectorstore
    if _vectorstore:
        _save()
    _vectorstore = None
