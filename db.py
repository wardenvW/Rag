from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, OptimizersConfig
from typing import List
from dataclasses import dataclass
import json
from pipeline import Chunk
import os


path = os.path.abspath("./vector_bd")

@dataclass
class ChunkMetaData:
    source: str
    author: str
    page: int  #Переделать в List[int]
    doc_hash: str

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
                "pages": meta.pages,
                "doc_hash": meta.doc_hash,
                "text": text[:100]
            })
        return json.dumps(res, ensure_ascii=False, indent=2)


class VectorStorage:
    def __init__(self, path: str = path, collection_name: str = "docs", dim: int = 1024) -> None:
        self.client: QdrantClient = QdrantClient(path=path)
        self.collection = collection_name
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config = VectorParams(size=dim, distance=Distance.COSINE),
                on_disk_payload=True,
            )

    def upsert(self, chunks: List[Chunk]) -> None:
            points = [
            PointStruct(
                id=chunk.id,
                vector=chunk.vector.tolist(),
                payload={
                    **chunk.payload,
                    "text": chunk.text
                }
            )
            for chunk in chunks
            ]
        
            if len(points) > 0:
                    points[0].id, len(points[0].vector), list(points[0].payload.keys())
            self.client.upsert(collection_name=self.collection, points=points)



    #добавить score_threshold если к примеру <0.4 то маленькая достоверность если 0.4<=x<=0.7средняя, >7 - высокая 
    def search(self, query_vector, top_k: int = 5) -> SearchResult:
        response = self.client.query_points(
            collection_name = self.collection,
            query = query_vector,
            with_payload = True,
            limit = top_k,
        )
        hits = response.points
        meta = []
        texts = []
        for p in hits:
            payload = getattr(p, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            author = payload.get("author", "")
            page = payload.get("page", -1)
            doc_hash = payload.get("doc_hash", "")
            if text:
                meta.append(ChunkMetaData(source, author, page, doc_hash))
                texts.append(text)
        
        result = SearchResult(meta, texts)
        return result
    
    def close(self):
        self.client.close()
#---------------------------------------------------------------    
#ПРОТЕСТИРОВАТЬ DENSE(СЕЙЧАС ЕСТЬ), SPARSE, HYBRID методы поиска
#---------------------------------------------------------------
#+RERANKING добавить
#Query expansion

# +Поменять вид Qdrant'a(сделать его по другому т.к этот вариант не сохраняет локально)