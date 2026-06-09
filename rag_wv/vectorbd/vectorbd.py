from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, SparseVectorParams, SparseVector, Prefetch, FusionQuery, Fusion, Filter, FieldCondition, MatchAny
from typing import List, Optional
from ..models import Chunk, ChunkMetaData, SearchResult, SparseVectorData
from ..config import QDRANT_PATH, QDRANT_URL, COLLECTION_NAME, VECTOR_DIM, USE_HYBRID, TOP_K, SAVE_HYBRID, USE_RERANKER
from ..reranker import Reranker
import logging

logger = logging.getLogger(__name__)
class VectorStorage:
    def __init__(self, path: str = QDRANT_PATH, url: str = QDRANT_URL, dim: int = VECTOR_DIM, on_disk: bool = True) -> None:
        self.collection = COLLECTION_NAME

        try:   
            if on_disk:
                logger.info("Initialize local(in-memory) Qdrant client")
                self.client: QdrantClient = QdrantClient(path=path)
                logger.info("Success")
            else:
                logger.info("Initialize local(web) Qdrant client")
                self.client: QdrantClient = QdrantClient(url=url)
                logger.info("Success")
                
            if not self.client.collection_exists(self.collection):
                logger.debug("Creating new collection")
                if SAVE_HYBRID:
                    logger.debug("option SAVE_HYBRID - True")
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
                    logger.debug(f"dim({dim}), distance(COSINE), on_disk_payload(True)")
                else:
                    logger.debug("option SAVE_HYBRID - False")
                    self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config = {"dense": VectorParams(size=dim, distance=Distance.COSINE)},
                    on_disk_payload=True,
                    )
                    logger.debug(f"dim({dim}), distance(COSINE), on_disk_payload(True)")
                logger.info(f"Collection created: {self.client.get_collection(self.collection)}")
            if USE_RERANKER:
                logger.info("Init reranker")
                self.reranker = Reranker()
            else:
                logger.debug("Not using reranker")
                self.reranker = None

        except Exception as e:
            logger.exception(f"Exception was occure: {e}")
            raise e

    def upsert(self, chunks: List[Chunk]) -> None:
            try:
                points = []
                logger.debug("Trying to upsert data to db")
                for chunk in chunks:
                        if SAVE_HYBRID:
                            vector_data = {
                                "dense": chunk.dense_vector,
                                "sparse": SparseVector(indices = chunk.sparse_vector.indices, values = chunk.sparse_vector.values)
                            }
                        else:
                            vector_data = {"dense": chunk.dense_vector}
                        
                        logger.debug(f"Adding PointStruct[id={chunk.id}, vector={vector_data}, payload={chunk.payload, chunk.text}]")
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
                point_quantity = len(points)
                if point_quantity > 0:
                    logger.debug(f"Trying to upsert -{point_quantity}- points")
                    self.client.upsert(collection_name=self.collection, points=points)
                    logger.info(f"Added -{point_quantity}-")
                    return
                logger.info("No data to upsert")
            except Exception as e:
                logger.exception(f"Exception occur: {e}")
                raise e


    def search(self, used_documents: List[str], query, query_dense, query_sparse: Optional[SparseVectorData] = None, top_k: int = TOP_K, debug: bool = False) -> List[SearchResult]:
        logger.info("Starting search")
        try:
            query_filter = None
            if used_documents:
                query_filter = Filter(
                    must = [
                        FieldCondition(
                            key="doc_hash",
                            match=MatchAny(any=used_documents)
                        )
                    ]
                )
                if debug:
                    logger.debug(f"Applied filter for docs: {query_filter}")


            if USE_HYBRID:
                if debug:
                    logger.debug(f"HYBRID, TOP_K={top_k}")
                    logger.debug(f"Query(dense) - {query_dense}")
                    logger.debug(f"Query(sparse) - {query_sparse}")

                response = self.client.query_points(
                    collection_name= self.collection,
                    prefetch= [
                        Prefetch(query=query_dense[0], using="dense",limit=top_k),

                        Prefetch(query=SparseVector(indices=query_sparse[0].indices, values=query_sparse[0].values), using="sparse", limit=top_k)
                    ],
                    query= FusionQuery(
                        fusion = Fusion.RRF
                    ),
                    query_filter=query_filter,
                    with_payload = True,
                    limit= top_k
                )
            else:
                if debug:
                    logger.debug(f"NON HYBRID, TOP_K={top_k}")
                    logger.debug(f"Query(dense) - {query_dense}")
                response = self.client.query_points(
                    collection_name = self.collection,
                    query = query_dense[0],
                    query_filter=query_filter,
                    with_payload = True,
                    limit = top_k,
                    using = "dense"
                )
            logger.info("Success")
            
            logger.debug(f"hits [{response.points}]")
            hits = response.points
            search_result: List[SearchResult] = []
            for p in hits:
                payload = getattr(p, "payload", None) or {}
                text = payload.get("text", "")
                logger.debug(f"payload[{payload}]")
                meta = ChunkMetaData(
                        source=payload.get("source", ""),
                        author=payload.get("author", list()),
                        page=payload.get("page", []),
                        doc_hash=payload.get("doc_hash", "")
                    )
                logger.debug(f"created metadata[{meta}]")
                search_result.append(SearchResult(meta=meta, text=text))

            if USE_RERANKER:
                logger.info("Reranker working ...")
                if self.reranker:
                    search_result = self.reranker.rerank(query, search_result)
                    logger.info("Success")

            logger.debug(f"search_result[{search_result}]")
            return search_result
        except Exception as e:
            logger.exception(f"Exception occur: {e}")
            raise e
        
    def close(self):
        logger.info("DB client closing")
        self.client.close()
        logger.info("Closed")