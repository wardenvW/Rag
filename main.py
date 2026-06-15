from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from rag_wv.api.routers import document_router, chat_router
from rag_wv.api.internal import admin_router
from rag_wv import Pipeline, RecursiveSplitter, Embedder, VectorStorage, init_logging
from rag_wv.db import Base, engine
from contextlib import asynccontextmanager
import logging

init_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.chunker = RecursiveSplitter()
    app.state.embedder = Embedder()
    app.state.vector_db = VectorStorage()
    app.state.pipeline = Pipeline(chunker = app.state.chunker, embedder = app.state.embedder, vector_db = app.state.vector_db)
    yield
    app.state.vector_db.close()

logger.info("Starting app")
app = FastAPI(lifespan=lifespan)


origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5173", #<-- Здесь React
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router, prefix="/documents", tags=['docs'])
app.include_router(chat_router, prefix='/chat', tags=['chat'])
app.include_router(admin_router, prefix='/admin', tags=['admin'])

app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{rest_of_path:path}")
async def serve_spa(rest_of_path: str):
    return FileResponse("frontend/dist/index.html")