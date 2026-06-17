from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Dict, Tuple, Callable
from ..models import DocumentType
from ..config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from pathlib import Path
from ..utils import get_handler
import logging

logger = logging.getLogger(__name__)

class RecursiveSplitter:
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP, separators: List[str] = ["\n\n", "\n", ". ", " ", ""]):
        self._splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, add_start_index=True, chunk_overlap = chunk_overlap)

    def change_chunk_params(self, doc_type: str) -> None:
        if doc_type == DocumentType.LEGAL.value:
            chunk_size = 2500
            chunk_overlap = 250
            separators = ["\n\n", "\nСтатья ", "\n", ". ", " ", ""]
        elif doc_type == DocumentType.TECH.value:
            chunk_size = 1500
            chunk_overlap = 150
            separators = ["\n\n", "\n", ". ", " ", ""]
        elif doc_type == DocumentType.FINANCE.value:
            chunk_size = 2000
            chunk_overlap = 200
            separators = ["\n\n", "\n", " ", ""]
        elif doc_type == DocumentType.OTHER.value:
            chunk_size = DEFAULT_CHUNK_SIZE
            chunk_overlap = DEFAULT_CHUNK_OVERLAP
            separators = ["\n\n", "\n", ". ", " ", ""]

        self._splitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)

    def chunk(self, doc: Path, doc_type: str) -> List[Tuple[str, Dict]]:
        try:
            filename_extension = doc.suffix 
            handler: Callable = get_handler(filename_extension)

            logger.info(f"Launching handler for ({filename_extension})")
            return handler(doc, doc_type, self._splitter)

        except Exception as e:
            logger.exception(f"Exception occur: {e}")
            raise e
