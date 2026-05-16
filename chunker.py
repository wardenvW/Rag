from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Dict, Any, Tuple

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
    def __init__(self, chunk_size: int = 512, overlap: int = 0, separators: List[str] = ["\n\n", "\n", ". ", " ", ""]):
        self._splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=chunk_size, chunk_overlap=overlap, add_start_index=True)
        self._chunk_size: int = chunk_size
        self._overlap: int = overlap
    
    def chunk(self, data: Dict[str, Any]) -> List[Tuple[str, Dict]]:
        try:
            pages = data["payload"]["pages"]
            author = data["payload"]["author"]
            source = data["payload"]["source"]

            results = []

            for page in pages:
                page_num = page["page"]
                text = page["text"]

                doc = Document(
                    page_content=text,
                    metadata={
                        "page": page_num,
                        "source": source,
                        "author": author
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

###
####
##### ЗДЕСЬ ОРГАНИЗОВАН ЧАНКИНГ 1ой СТРАНИЦЫ И ЗАТЕМ ПЕРЕХОД НА СЛЕДУЮУЩУЮ, ПРОТЕСТИТЬ ЭФФЕКТИВНОСТЬ И УВЕЛИЧИТЬ ДЛИНУ БЛОКА(КОЛ-ВО СТРАНИЦ ОДНОВРЕМЕННО ОБРАБАТЫВАЮЩИХСЯ) ПРИ НАДОБНОСТИ 
####
###