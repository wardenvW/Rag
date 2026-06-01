import logging
import uuid
from typing import List
from ..models import Chunk
from pathlib import Path
from ..utils import data_normalize

logger = logging.getLogger(__name__)
class Pipeline:
    def __init__(self, chunker, embedder, vector_db) -> None:
        self.chunker = chunker 
        self.embedder = embedder
        self.vector_db = vector_db 

    def process(self, data: List[Path]) -> None:
        for doc in data:
            try:
                logger.info("Data normalize proccess")
                normalized_data = data_normalize(doc)
                logger.info("Success")

                logger.info("Chunking...")
                chunk_data = self.chunker.chunk(normalized_data)
                logger.info("Ready")
                chunk_texts = [chunk_text for chunk_text, _ in chunk_data]
                logger.info("Starting embedding")
                vectors = self.embedder.embed(chunk_texts)
                logger.info("Embedded")

                ready_chunks = []
                for (chunk_text, chunk_meta), d_vector, sp_vector in zip(chunk_data, vectors["dense"], vectors["sparse"]):
                    unique_str = f"{chunk_meta['doc_hash']}_{chunk_text}"
                    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_str))
                    
                    chunk = Chunk(text=chunk_text, dense_vector=d_vector, sparse_vector=sp_vector, payload=chunk_meta, id=uid)
                    ready_chunks.append(chunk)

                self.vector_db.upsert(ready_chunks)
            except Exception as e:
                logger.exception(f"Exception occur: {e}")
                raise e
#sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng В ОБЯЗАТЕЛЬНОМ ПОРЯДКЕ, чтобы установился движок OCR занимающийся распознаванием трудного текста, таблиц и тд