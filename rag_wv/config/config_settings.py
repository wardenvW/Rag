import os
import pathlib
import logging
from typing import List
from dotenv import load_dotenv

# --- Корневая папка(пути) ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR/".env")

# --- Параметры Embedding модели ---
EMB_MODEL_NAME: str = os.getenv("EMB_MODEL_NAME")
DEFAULT_BATCH_SIZE: int = 32

SAVE_HYBRID: bool = True #!!!НЕ ИЗМЕНЯТЬ ПАРАМЕТР!!!
USE_HYBRID: bool = True 


# --- Параметры векторной БД (Qdrant) ---
QDRANT_PATH: str = BASE_DIR / os.getenv("QDRANT_PATH")
QDRANT_URL: str = os.getenv("QDRANT_URL")
DOCUMENTS_PATH: str = BASE_DIR / "documents"
COLLECTION_NAME: str = "docs"
VECTOR_DIM: int = 1024
TOP_K: int = 25

# --- Параметры Chunker'а ---
DEFAULT_CHUNK_SIZE: int = 1000
DEFAULT_CHUNK_OVERLAP: int = 100

# --- Reranker и всё с ним связанное ---
RERANKER_NAME: str = "qilowoq/bge-reranker-v2-m3-en-ru"
USE_RERANKER: bool = True
TOP_N: int = 10

# --- LLM API KEY ---
API_KEY: str = os.getenv("API_KEY")

# --- Разрешённые типы файлов ---
ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ...]

# --- Логгирование ---
LOG_LEVEL = logging.DEBUG
LOG_FILE: str = "app.log"
def init_logging() -> None:
    LOG_FORMAT = '%(asctime)s | %(levelname)-7s | %(name)s - %(message)s'
    DATE_FORMAT = '%Y/%m/%d %H:%M:%S'


    logging.basicConfig(
        level=LOG_LEVEL,
        format =LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(filename=BASE_DIR / LOG_FILE, encoding="utf-8")
        ],
    )
    logging.getLogger("httpx").setLevel(logging.FATAL)
    logging.getLogger("httpcore.http11").setLevel(logging.FATAL)
    logging.getLogger("httpcore.connection").setLevel(logging.FATAL)
    logging.getLogger("sentence_transformers.base.model").setLevel(logging.FATAL)
    logging.getLogger("FlagEmbedding.finetune.embedder.encoder_only.m3.runner").setLevel(logging.FATAL)
    logging.getLogger("huggingface_hub.utils._http").setLevel(logging.FATAL)