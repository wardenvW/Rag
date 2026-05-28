from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

@dataclass
class SparseVectorData:
    indices: List[int]
    values: List[float]

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
    def __init__(self, text: str, dense_vector: List[float], sparse_vector: Optional[SparseVectorData], payload: Dict[str, Any], id: str)-> None: # add an annotation to 'sparse_vector'
        self.text: str = text
        self.dense_vector: List[float] = dense_vector
        self.sparse_vector: Optional[SparseVectorData] = sparse_vector
        self.payload: Dict[str, Any]= payload
        self.id: str = id

    def __eq__(self, other) -> bool:
        return (isinstance(other, Chunk)) and self.id == other.id
    
class SearchResult:
    def __init__(self, meta: ChunkMetaData, text: str) -> None:
        self.meta: ChunkMetaData = meta
        self.text: str =  text
        self.score: Optional[float] = None

    def __repr__(self) -> str:
        return json.dumps({
            "source": self.meta.source,
            "author": self.meta.author,
            "pages": self.meta.page,
            "doc_hash": self.meta.doc_hash,
            "text": self.text[:100],
            "score": self.score
        }, ensure_ascii=False, indent=2)