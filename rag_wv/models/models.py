from dataclasses import dataclass
from typing import List


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