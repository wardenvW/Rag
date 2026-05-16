from typing import List, Dict, Any
from pathlib import Path, PurePath
from hashlib import sha256
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
    

def data_normalize(document) -> Dict[str, Any]:
    try:
        reader = PdfReader(document)
        pages_data = [
            (
                index, 
                normalize_text(page.extract_text()),       
            ) 
            for index, page in enumerate(reader.pages)

        ]

        source = PurePath(document).name
        
        author_pages = [0, 1, -1, -2] if len(pages_data) > 4 else [0, -1]
        author_mentioned_pages = " ".join(pages_data[page][1] for page in author_pages)

        author = reader.metadata.author if reader.metadata.author else extract_author(author_mentioned_pages)

        data = {
            "payload": {
                "source": source,
                "author": author,
                "pages": [
                    {
                        "page": index,
                        "text": text
                    }
                    for index, text in pages_data
                ],
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
        return (isinstance(other, Chunk)) and self.id == other.id




class Pipeline:
    def __init__(self, chunker, embedder, vector_db) -> None:
        self.chunker = chunker 
        self.embedder = embedder
        self.vector_db = vector_db 

    @staticmethod #метод устарел  {X}не работает для Qdrant{X} ??? Добавить позже в payload
    def get_hash(data) -> str:
        return sha256(data.encode()).hexdigest()

    def process(self, data: List[Path]) -> None:
            for doc in data:
                try:
                    normalized_data = data_normalize(doc)
                    print("STEP 1")
                    chunk_data = self.chunker.chunk(normalized_data)
                    print("CHUNKS:", len(chunk_data))
                    print("DOC:", doc)

                    chunk_texts = [chunk_text for chunk_text, _ in chunk_data]
                    print("STEP 2")
                    print("ABOUT TO EMBED:", len(chunk_texts))
                    vectors = self.embedder.embed(chunk_texts)
                    print("VECTORS:", len(vectors))
                    print(f"EMBED DONE")

                    ready_chunks = []
                    for (chunk_text, chunk_meta), vector in zip(chunk_data, vectors):
                        hash_v = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_text))

                        chunk = Chunk(text=chunk_text, vector=vector, payload=chunk_meta, id=hash_v)

                        ready_chunks.append(chunk)

                    self.vector_db.upsert(ready_chunks)
                except Exception as e:
                    print(e)
                    raise
