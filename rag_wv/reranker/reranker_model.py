from sentence_transformers import CrossEncoder
from typing import List
from ..config import RERANKER_NAME, TOP_N
from ..models import SearchResult

class Reranker:
    def __init__(self) -> None:
        self.model: CrossEncoder = CrossEncoder(RERANKER_NAME)
    
    def rerank(self, query: str, search_result: List[SearchResult]):
        res = self.model.predict([[query, data.text] for data in search_result])

        for sc, obj in zip(res, search_result):
            obj.score = float(sc)
        
        return sorted(search_result, key= lambda x: x.score, reverse=True)[:TOP_N]
