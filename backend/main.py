from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import get_settings
from routers import auth, query, upload
import os

settings = get_settings()

app = FastAPI(
    title="Enterprise Knowledge Bot",
    description="RAG-powered chatbot for internal documents, wikis, and databases",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# Serve React frontend — must be last
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "Enterprise Knowledge Bot API — visit /docs"}
