from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np
import json

@dataclass
class PageSpan:
    page: int
    start: int
    end: int

@dataclass
class ChunkMetaData:
    source: str
    author: List[str]
    page: List[int]
    doc_hash: str

class Chunk:
    def __init__(self, text: str, dense_vector: np.ndarray, sparse_vector ,payload: Dict[str, Any], id: str)-> None: # add an annotation to 'sparse_vector'
        self.text: str = text
        self.dense_vector: np.ndarray = dense_vector
        self.sparse_vector = sparse_vector  # add an annotation
        self.payload: Dict[str, Any]= payload
        self.id: str = id

    def __eq__(self, other) -> bool:
        return (isinstance(other, Chunk)) and self.id == other.id
    
class SearchResult:
    def __init__(self, meta: List[ChunkMetaData], chunks_text: List[str]) -> None:
        self.meta: List[ChunkMetaData] = meta
        self.text: List[str] =  chunks_text

    def __repr__(self) -> str:
        res = []
        for meta, text in zip(self.meta, self.text):
            res.append({
                "source": meta.source,
                "author": meta.author,
                "pages": meta.page,
                "doc_hash": meta.doc_hash,
                "text": text[:100]
            })
        return json.dumps(res, ensure_ascii=False, indent=2)