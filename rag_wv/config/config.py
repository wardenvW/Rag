import os
import pathlib
import logging
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR/".env")

EMB_MODEL_PATH = BASE_DIR / os.getenv("EMB_MODEL_PATH")

QDRANT_PATH = BASE_DIR / os.getenv("QDRANT_PATH")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "docs"

VECTOR_DIM = 1024
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 0
DEFAULT_BATCH_SIZE = 32

API_KEY = os.getenv("API_KEY")

ALLOWED_FILE_TYPES = [".pdf", ".doc", ".docx", ...]

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
        encoding='utf-8',
    )