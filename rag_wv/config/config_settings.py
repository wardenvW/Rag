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
COLLECTION_NAME: str = "docs"
VECTOR_DIM: int = 1024
TOP_K: int = 5

# --- Параметры Chunker'а ---
DEFAULT_CHUNK_SIZE: int = 512
DEFAULT_CHUNK_OVERLAP: int = 0

# --- LLM API KEY ---
API_KEY: str = os.getenv("API_KEY")

# --- Разрешённые типы файлов ---
ALLOWED_FILE_TYPES: List[str] = [".pdf", ".doc", ".docx", ...]

# --- Логгирование ---
LOG_LEVEL = logging.DEBUG
def init_logging() -> None:
    LOG_FORMAT = '%(asctime)s | %(levelname)-7s | %(name)s - %(message)s'
    DATE_FORMAT = '%Y/%m/%d %H:%M:%S'


    logging.basicConfig(
        level=LOG_LEVEL,
        format =LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(filename=BASE_DIR / "app.log", encoding="utf-8")
        ],
    )