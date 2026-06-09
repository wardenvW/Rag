from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag_wv.api.routers import document_router, chat_router
from rag_wv.api.internal import admin_router
from rag_wv import Pipeline, RecursiveSplitter, Embedder, VectorStorage, init_logging
from rag_wv.db import Base, engine
from contextlib import asynccontextmanager

init_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.chunker = RecursiveSplitter()
    app.state.embedder = Embedder()
    app.state.vector_db = VectorStorage()
    app.state.pipeline = Pipeline(chunker = app.state.chunker, embedder = app.state.embedder, vector_db = app.state.vector_db)
    yield
    app.state.vector_db.close()

app = FastAPI(lifespan=lifespan)


origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000" #<-- Здесь React
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