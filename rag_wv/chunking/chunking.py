from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Dict, Any, Tuple
from ..models import PageSpan, DocumentType
from ..config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
import logging

logger = logging.getLogger(__name__)

def create_page_mapping(pages: List[Dict[str, Any]]) -> List[PageSpan]:
    current = 0
    result = []

    for page in pages:
        start = current
        end = start + len(page["text"])

        p_span = PageSpan(page["page"], start, end)
        result.append(p_span)

        current = end + 1

    return result

def get_chunk_pages(chunk_start: int, chunk_end: int, mapping_list: List[PageSpan]) -> List[int]:
    pages = []
    for p in mapping_list:
        if (chunk_start < p.end and chunk_end > p.start):
            pages.append(p.page)

    return pages

#
##
### Попробовать Оптимизировать поиск (сейчас O(n))
##
#
class RecursiveSplitter:
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP, separators: List[str] = ["\n\n", "\n", ". ", " ", ""]):
        self._splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, add_start_index=True, chunk_overlap = chunk_overlap)

    def change_chunk_params(self, doc_type: str) -> None:
        if doc_type == DocumentType.LEGAL.value:
            chunk_size = 2500
            chunk_overlap = 250
            separators = ["\n\n", "\nСтатья ", "\n", ". ", " ", ""]
        elif doc_type == DocumentType.TECH.value:
            chunk_size = 1500
            chunk_overlap = 150
            separators = ["\n\n", "\n", ". ", " ", ""]
        elif doc_type == DocumentType.FINANCE.value:
            chunk_size = 2000
            chunk_overlap = 200
            separators = ["\n\n", "\n", " ", ""]
        elif doc_type == DocumentType.CRIMINALIST.value:
            chunk_size = 1400
            chunk_overlap = 150
            separators = ["\n\n", "\nПодозреваемый ", "\n", ". ", " ", ""]
        elif doc_type == DocumentType.OTHER.value:
            chunk_size = DEFAULT_CHUNK_SIZE
            chunk_overlap = DEFAULT_CHUNK_OVERLAP
            separators = ["\n\n", "\n", ". ", " ", ""]

        self._splitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)

    def chunk(self, data: Dict[str, Any], doc_type: str) -> List[Tuple[str, Dict]]:
        try:
            pages = data["payload"]["pages"]
            author = data["payload"]["author"]
            source = data["payload"]["source"]
            doc_hash = data["payload"]["doc_hash"]
            doc_type = data["payload"]["type"]

            results = []
            full_text = ""


            full_text = " ".join(page["text"] for page in pages) + " "

            doc = Document(
                page_content= full_text,
                metadata={
                    "source": source,
                    "author": author,
                    "doc_hash": doc_hash,
                    "type": doc_type,
                }
            )
            logger.info("Creating page mapping")
            map_list = create_page_mapping(pages)
            logger.info("Created")
            
            logger.info("Document splitting")
            chunks = self._splitter.split_documents([doc])
            logger.info("Ready")

            for c in chunks:
                chunk_start = c.metadata.get("start_index", None)
                chunk_end = chunk_start + len(c.page_content)
                results.append(
                    (
                        c.page_content,
                        {
                            "page": get_chunk_pages(chunk_start, chunk_end, map_list),
                            **c.metadata
                        }
                    )
                )

            return results

        except Exception as e:
            logger.exception(f"Exception occur: {e}")
            raise e
