from typing import List, Dict, Any
from pathlib import Path, PurePath
from hashlib import file_digest
from pypdf import PdfReader
import re
import numpy as np
import uuid

def extract_author(text: str) -> List[str]:
    pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.[А-ЯЁ]\.|[А-ЯЁ]\.[А-ЯЁ]\.\s[А-ЯЁ][а-яё]+'
    authors = set(re.findall(pattern, text))
    normalized = set()
    for author in authors:
        parts = author.split()
        if parts[0].endswith('.'):
            normalized.add(f"{parts[1]} {parts[0]}")
        else:
            normalized.add(f"{parts[0]} {parts[1]}")

    return list(normalized)

def normalize_text(txt: str) -> str:
    text = txt or ""
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text

def get_doc_hash(document) -> str:
    digest = "sha256"
    with open(document, 'rb') as f:
        digest = file_digest(f, "sha256")
    return digest.hexdigest()

def data_normalize(document) -> Dict[str, Any]:    
    try:
        reader = PdfReader(document)
        pages_data = [
            {
                "page": index, 
                "text": normalize_text(page.extract_text()),       
            } 
            for index, page in enumerate(reader.pages, start=1)
        ]

        source = PurePath(document).name
        
        author_pages = [0, 1, -1, -2] if len(pages_data) > 4 else [0, -1]
        author_mentioned_pages = " ".join(pages_data[page]["text"] for page in author_pages)

        author = reader.metadata.author if reader.metadata.author else extract_author(author_mentioned_pages)

        d_hash = get_doc_hash(document)

        data = {
            "payload": {
                "source": source,
                "author": author,
                "pages": pages_data,
                "doc_hash": d_hash,
            },
        }

        return data
    except Exception as e:
        print(e)
        raise

class Chunk:
    def __init__(self, text: str, vector: np.ndarray, payload: Dict[str, Any], id: str)-> None:
        self.text: str = text
        self.vector: np.ndarray = vector
        self.payload: Dict[str, Any]= payload
        self.id: str = id

    def __eq__(self, other) -> bool:
        return (isinstance(other, Chunk)) and self.payload["doc_hash"] == other.payload["doc_hash"]

class Pipeline:
    def __init__(self, chunker, embedder, vector_db) -> None:
        self.chunker = chunker 
        self.embedder = embedder
        self.vector_db = vector_db 

    def process(self, data: List[Path]) -> None:
            for doc in data:
                try:
                    normalized_data = data_normalize(doc)
                    chunk_data = self.chunker.chunk(normalized_data)

                    chunk_texts = [chunk_text for chunk_text, _ in chunk_data]
                    vectors = self.embedder.embed(chunk_texts)

                    ready_chunks = []
                    for (chunk_text, chunk_meta), vector in zip(chunk_data, vectors):
                        uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_text))

                        chunk = Chunk(text=chunk_text, vector=vector, payload=chunk_meta, id=uid)

                        ready_chunks.append(chunk)

                    self.vector_db.upsert(ready_chunks)
                except Exception as e:
                    print(e)
                    raise

#УБРАТЬ НОРМАЛИЗАЦИЮ ТЕКСТА, СДЕЛАЙ ЕЁ более мягкой и починить страницы(через off set'ы)