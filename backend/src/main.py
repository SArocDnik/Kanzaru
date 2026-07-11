from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.deps import init_db
from src.api.routes import projects, chapters, upload, llm, characters, translate
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Kanzaru",
    description="Story translation app with TTS",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(chapters.router)
app.include_router(upload.router)
app.include_router(llm.router)
app.include_router(characters.router)
app.include_router(translate.router)


@app.get("/health")
def health():
    return {"status": "ok"}
