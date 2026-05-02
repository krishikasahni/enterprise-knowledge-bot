from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import auth, query, upload

settings = get_settings()

app = FastAPI(
    title="Enterprise Knowledge Bot",
    description="RAG-powered chatbot for internal documents, wikis, and databases",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(upload.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


@app.get("/")
async def root():
    return {"message": "Enterprise Knowledge Bot API — visit /docs for Swagger UI"}
