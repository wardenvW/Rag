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
class RecursiveSplitter:
    def __init__(self, chunk_size: int = 2500, separators: List[str] = ["\n\n", "\n", ". ", " ", ""]):
        self._splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, add_start_index=True, chunk_overlap = 0)
        self._chunk_size: int = chunk_size
    
    def chunk(self, data: Dict[str, Any]) -> List[Tuple[str, Dict]]:
        try:
            pages = data["payload"]["pages"]
            author = data["payload"]["author"]
            source = data["payload"]["source"]
            doc_hash = data["payload"]["doc_hash"]

            results = []
            full_text = ""


            for page in pages:
                text = page["text"]
                full_text += text + " "

            doc = Document(
                page_content= full_text,
                metadata={
                    "source": source,
                    "author": author,
                    "doc_hash": doc_hash,
                }
            )
            map_list = create_page_mapping(pages)

            chunks = self._splitter.split_documents([doc])

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
            print(e)
            raise


###
#### Также сделать выбор (Для определённых документов chunk_size, overlap) Прим. Юр.Документы(2000, 200), Тех.Литература и тд тп
##### Затестить Doсling для сложных страниц
####
###

