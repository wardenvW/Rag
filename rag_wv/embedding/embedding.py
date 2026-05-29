from FlagEmbedding import BGEM3FlagModel
from typing import List, Dict
from ..models import SparseVectorData
from ..config import EMB_MODEL_NAME, DEFAULT_BATCH_SIZE, SAVE_HYBRID

class Embedder:
    def __init__(self) -> None:
        self.model: BGEM3FlagModel = BGEM3FlagModel(model_name_or_path=EMB_MODEL_NAME, use_fp16=True, batch_size=DEFAULT_BATCH_SIZE, return_dense=True, return_sparse=SAVE_HYBRID, return_colbert_vecs=False, trust_remote_code=True) #добавить batch_size в конфиг
        self.save_hybrid: bool = SAVE_HYBRID

    def embed(self, chunks: List[str]) -> Dict[str, List]:
        try:
            encode_result = self.model.encode(chunks, batch_size=DEFAULT_BATCH_SIZE, return_dense=True, return_sparse=self.save_hybrid)

            sparse_list = []
            if 'lexical_weights' in encode_result:
                sparse_list = [SparseVectorData(indices = [int(k) for k in chunk_weights.keys()], values = [float(v) for v in chunk_weights.values()]) for chunk_weights in encode_result["lexical_weights"]]
            
            result = {"dense": encode_result["dense_vecs"].tolist()[0], "sparse": sparse_list[0]}
            return result
        except Exception as e:
            pass
#ДОБАВИТЬ ЛОГИРОВАНИЕ + ОБРАБОТКУ Exception
