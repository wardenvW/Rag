from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean
from datetime import datetime
from enum import Enum
from rag_wv.db import Base
from uuid import UUID
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
    type: str

class Chunk:
    def __init__(self, text: str, dense_vector: List[float], sparse_vector: Optional[SparseVectorData], payload: Dict[str, Any], id: str)-> None:
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

    def __str__(self) -> str:
            return json.dumps({
                "source": self.meta.source,
                "author": self.meta.author,
                "pages": self.meta.page,
                "doc_hash": self.meta.doc_hash,
                "type": self.meta.type,
                "text": self.text[:100] + "...",
                "score": self.score
            }, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        return f"SearchResult[source={self.meta.source}, score={self.score}]"





# =====================================================================
#                           PYDANTIC МОДЕЛИ и ДРУГОЕ
# =====================================================================
class SearchResultResponse(BaseModel):
    source: str
    author: List[str]
    pages: List[int]
    text: str
    score: Optional[float] = None

    @classmethod
    def from_rag_results(cls, result: SearchResult):
        return cls(
            source=result.meta.source,
            author=result.meta.author,
            pages=result.meta.page,
            text=result.text,
            score=result.score
        )
    
class QueryRequest(BaseModel):
    query: str

class DocumentType(str, Enum):
    LEGAL = "legal"
    TECH = "tech"
    FINANCE = "finance"
    CRIMINALIST = "criminalist"
    OTHER = "other"

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    UPLOADED = "uploaded"
class DocumentResponse(BaseModel):
    id: str
    filename: str
    filesize: int
    status: DocumentStatus
    is_using: bool
    doc_type: DocumentType
    uploaded_at: datetime

class DeleteResponse(BaseModel):
    id: str

class ChatQueryRequest(BaseModel):
    query: str


"""
id - document hash(for painless search within RAG )
id - хэш документа(для безболезненного поиска с RAG системой)
"""
class DocumentNode(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64),primary_key=True)  
    filename: Mapped[str] = mapped_column(String(128), index=True)
    filesize: Mapped[int]
    status: Mapped[str] = mapped_column(String(10), index=True, default=DocumentStatus.PROCESSING)
    is_using: Mapped[bool] = mapped_column(Boolean ,index=True, default=True)
    doc_type: Mapped[str] = mapped_column(String(8), index=True, default=DocumentType.OTHER)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)