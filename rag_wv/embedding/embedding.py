from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class Embedder:
    def __init__(self, path: str = "./model") -> None:
        self.model: SentenceTransformer = SentenceTransformer(path)

    def embed(self, chunks: List[str], batch_size: int = 32) -> List[np.ndarray]:
        embeddings = self.model.encode(
            chunks,
            normalize_embeddings=True,
            convert_to_numpy=True,
            batch_size=batch_size      #Изменить batch_size в зависимости от мощностей вашей системы
        )
        return embeddings