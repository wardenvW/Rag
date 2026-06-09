import logging
import uuid
import os
from dotenv import load_dotenv
from google.genai import Client, types
from pathlib import Path
from typing import List, Iterator
from ..models import Chunk, DocumentType
from ..utils import data_normalize
from ..prompt import build_prompt, build_promptv2

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")

class Pipeline:
    def __init__(self, chunker, embedder, vector_db) -> None:
        self.chunker = chunker 
        self.embedder = embedder
        self.vector_db = vector_db
        self.llm = Client(api_key=API_KEY)

    def process(self, data: List[Path], d_type) -> None:
        for doc in data:
            try:
                logger.info("Data normalize proccess")
                normalized_data = data_normalize(doc, d_type)
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
            
    def stream_answer(self, query: str, used_documents: List[str]) -> Iterator:
        query_vector = self.embedder.embed([query])
        results = self.vector_db.search(used_documents, query, query_vector["dense"], query_vector["sparse"], debug=True)
        if results:
            context = "\n\n".join(f"[{obj.meta.source} | Возможные страницы: {obj.meta.page}]\n{obj.text}" for obj in results)
            persona_keys = {obj.meta.type for obj in results}

            instruction, prompt = build_promptv2(context=context, query=query, persona_key=persona_keys)

            for chunk in self.llm.models.generate_content_stream(model="gemma-4-31b-it", contents=prompt, config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.5)):
                yield chunk.text
        else:
            context = "Контекста нет, отвечай на базе своих знаний. "
            persona_keys = {DocumentType.OTHER.value}

            instruction, prompt = build_promptv2(context=context, query=query, persona_key=persona_keys)


            for chunk in self.llm.models.generate_content_stream(model="gemma-4-31b-it", contents=prompt, config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.5)):
                yield chunk.text