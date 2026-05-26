from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, SparseVectorParams, SparseVector, Prefetch, FusionQuery, Fusion
from typing import List
from ..models import Chunk, ChunkMetaData, SearchResult
from ..config import QDRANT_PATH, QDRANT_URL, COLLECTION_NAME, VECTOR_DIM, USE_HYBRID, TOP_K, SAVE_HYBRID, USE_RERANKER
from ..reranker import Reranker

class VectorStorage:
    def __init__(self, path: str = QDRANT_PATH, url: str = QDRANT_URL, dim: int = VECTOR_DIM, in_memory: bool = True) -> None:
        self.collection = COLLECTION_NAME

        try:   
            if in_memory:
                self.client: QdrantClient = QdrantClient(path=path)
            else:
                self.client: QdrantClient = QdrantClient(url=url)
                
            if not self.client.collection_exists(self.collection):
                if SAVE_HYBRID:
                    self.client.create_collection(
                        collection_name=self.collection,
                        vectors_config={
                            "dense": VectorParams(size=dim, distance=Distance.COSINE),
                        },
                        sparse_vectors_config={
                            "sparse": SparseVectorParams()
                        },
                        on_disk_payload=True,
                    )
                else:
                        self.client.create_collection(
                        collection_name=self.collection,
                        vectors_config = {"dense": VectorParams(size=dim, distance=Distance.COSINE)},
                        on_disk_payload=True,
                    )
        except Exception as e:
            pass

    def upsert(self, chunks: List[Chunk]) -> None:
            try:
                points = []

                for chunk in chunks:
                        if SAVE_HYBRID:
                            vector_data = {
                                "dense": chunk.dense_vector.tolist(),
                                "sparse": SparseVector(indices = chunk.sparse_vector.indices, values = chunk.sparse_vector.values)
                            }
                        else:
                            vector_data = {"dense": chunk.dense_vector.tolist()}

                        points.append(
                            PointStruct(
                                id = chunk.id,
                                vector = vector_data,
                                payload={
                                    **chunk.payload,
                                    "text": chunk.text
                                }
                            )
                        )

                if len(points) > 0:
                    self.client.upsert(collection_name=self.collection, points=points)
            except Exception as e:
                pass



    #добавить score_threshold если к примеру <0.4 то маленькая достоверность если 0.4<=x<=0.7средняя, >7 - высокая  //ЭТО в DEBUG/INFO
    def search(self, query, query_dense, query_sparse = None, top_k: int = TOP_K) -> List[SearchResult]: #Потестить добавить Matryoshka  
        if USE_HYBRID:
            response = self.client.query_points(
                collection_name= self.collection,
                prefetch= [
                    Prefetch(query=query_dense, using="dense",limit=top_k),

                    Prefetch(query=query_sparse, using="sparse", limit=top_k)
                ],
                query= FusionQuery(
                    fusion = Fusion.RRF
                ),
                with_payload = True,
                limit= top_k
            )
        else:
            response = self.client.query_points(
                collection_name = self.collection,
                query = query_dense,
                with_payload = True,
                limit = top_k,
                using = "dense"
            )
        
        hits = response.points
        search_result: List[SearchResult] = []
        for p in hits:
            payload = getattr(p, "payload", None) or {}
            text = payload.get("text", "")

            meta = ChunkMetaData(
                    source=payload.get("source", ""),
                    author=payload.get("author", ""),
                    page=payload.get("page", []),
                    doc_hash=payload.get("doc_hash", "")
                )
            search_result.append(SearchResult(meta=meta, text=text))

        if USE_RERANKER:
            rkr = Reranker()
            search_result = rkr.rerank(query, search_result)

        return search_result
    
    def close(self):
        self.client.close()