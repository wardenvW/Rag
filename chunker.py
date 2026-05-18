from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class PageSpan:
    page: int
    start: int
    end: int


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


class FixedSplitter:
    def __init__(self, chunk_size: int = 100, overlap: int = 10) -> None:
        self._chunk_size: int = chunk_size
        self._overlap: int = overlap

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self._chunk_size - self._overlap):
            chunk = " ".join(words[i:i + self._chunk_size])
            chunks.append(chunk)
        return chunks

class RecursiveSplitter:
    def __init__(self, chunk_size: int = 512, separators: List[str] = ["\n\n", "\n", ". ", " ", ""]):
        self._splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, add_start_index=True, chunk_overlap = 0)
        self._chunk_size: int = chunk_size
    
    def chunk(self, data: Dict[str, Any]) -> List[Tuple[str, Dict]]:
        try:
            pages = data["payload"]["pages"]
            author = data["payload"]["author"]
            source = data["payload"]["source"]
            doc_hash = data["payload"]["doc_hash"]

            results = []

            for page in pages:
                page_num = page["page"]
                text = page["text"]

                doc = Document(
                    page_content=text,
                    metadata={
                        "page": page_num,
                        "source": source,
                        "author": author,
                        "doc_hash": doc_hash,
                    }
                )

                chunks = self._splitter.split_documents([doc])

                for c in chunks:
                    results.append(
                        (
                            c.page_content,
                            {
                                **c.metadata  #Добавляем(раскрываем) все мета-данные отдельных чанков 
                            }
                        )
                    )

            return results

        except Exception as e:
            print(e)
            raise

    def chunk2(self, data: Dict[str, Any]) -> List[Tuple[str, Dict]]:
        try:
            pages = data["payload"]["pages"]
            author = data["payload"]["author"]
            source = data["payload"]["source"]
            doc_hash = data["payload"]["doc_hash"]

            results = []
            full_text = ""

            for page in pages:
                text = page["text"]
                full_text += text + "\n"

            doc = Document(
                page_content=full_text,

            )

            chunks = self._splitter.split_documents([doc])

            for c in range(3):
                start = chunks[c].metadata.get("start_index", None)

                chunk = chunks[c].page_content

                debug = {
                    "start": start,
                    "end": start + len(chunks[c].page_content),
                    "text": chunks[c].page_content,
                    
                }

                results.append((debug))
            print(create_page_mapping(pages))
            print(results)
        except Exception as e:
            print(e)
            raise
###
####
##### ЗДЕСЬ ОРГАНИЗОВАН ЧАНКИНГ 1ой СТРАНИЦЫ И ЗАТЕМ ПЕРЕХОД НА СЛЕДУЮУЩУЮ, ПРОТЕСТИТЬ ЭФФЕКТИВНОСТЬ И УВЕЛИЧИТЬ ДЛИНУ БЛОКА(КОЛ-ВО СТРАНИЦ ОДНОВРЕМЕННО ОБРАБАТЫВАЮЩИХСЯ) ПРИ НАДОБНОСТИ 
####
###