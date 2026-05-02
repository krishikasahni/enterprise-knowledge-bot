from typing import List, AsyncIterator
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are an expert enterprise knowledge assistant. \
Answer questions accurately using ONLY the provided context documents. \
If the answer is not in the context, say "I don't have enough information in the knowledge base to answer that."

Always cite the source(s) you used at the end of your answer in this format:
📎 Sources: [source1], [source2]

Be concise, professional, and helpful."""

HUMAN_TEMPLATE = """Context documents:
{context}

Question: {question}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_TEMPLATE),
])


def _format_context(docs: List[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        src = doc.metadata.get("source", "unknown")
        parts.append(f"[Doc {i} | {src}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_key=settings.openai_api_key,
        model="gpt-4o",
        temperature=0.2,
        streaming=streaming,
    )


async def answer(question: str, docs: List[Document]) -> str:
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()
    return await chain.ainvoke({
        "context": _format_context(docs),
        "question": question,
    })


async def answer_stream(question: str, docs: List[Document]) -> AsyncIterator[str]:
    llm = get_llm(streaming=True)
    chain = prompt | llm | StrOutputParser()
    async for chunk in chain.astream({
        "context": _format_context(docs),
        "question": question,
    }):
        yield chunk
