from dotenv import load_dotenv
load_dotenv()
from FlagEmbedding import BGEM3FlagModel
from typing import List
from ..config import EMB_MODEL_NAME, DEFAULT_BATCH_SIZE, SAVE_HYBRID

class Embedder:
    def __init__(self) -> None:
        self.model: BGEM3FlagModel = BGEM3FlagModel(model_name_or_path=EMB_MODEL_NAME, use_fp16=True, batch_size=DEFAULT_BATCH_SIZE, return_dense=True, return_sparse=SAVE_HYBRID, trust_remote_code=True) #добавить batch_size в конфиг
        self.save_hybrid: bool = SAVE_HYBRID

    def embed(self, chunks: List[str]):
        try:
            result = self.model.encode(chunks, batch_size=DEFAULT_BATCH_SIZE, return_dense=True, return_sparse=self.save_hybrid)
            return result
        except Exception as e:
            pass
#ДОБАВИТЬ ЛОГИРОВАНИЕ + ОБРАБОТКУ Exception
