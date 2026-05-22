from typing import List, Dict, Any
from pathlib import Path, PurePath
from hashlib import file_digest
from models import Chunk
import pymupdf4llm
import re
import uuid

def extract_author(text: str) -> List[str]:
    pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.[А-ЯЁ]\.|[А-ЯЁ]\.[А-ЯЁ]\.\s[А-ЯЁ][а-яё]+'
    authors = set(re.findall(pattern, text))
    normalized = set()
    for author in authors:
        parts = author.split()
        if parts[0].endswith('.'):
            normalized.add(f"{parts[1]} {parts[0]}")
        else:
            normalized.add(f"{parts[0]} {parts[1]}")

    return list(normalized)

def clean_pdf_text(text: str) -> str:
    text = re.sub(r"==> picture \[\d+ x \d+\] <==", "\n[ИЗОБРАЖЕНИЕ]\n", text)

    text = re.sub(r"----- Start of picture text -----", "", text)
    text = re.sub(r"----- End of picture text -----", "", text)

    text = re.sub(r"<br>", "", text)
    
    return text.strip()

def get_doc_hash(document) -> str:
    with open(document, 'rb') as f:
        digest = file_digest(f, "sha256")
    return digest.hexdigest()

def data_normalize(document) -> Dict[str, Any]:    
    try:
        pages = pymupdf4llm.to_text(document, ocr_language = "rus+eng", page_chunks = True)
        print(pages)
        pages_data = [
            {
                "page": page["metadata"]["page_number"], 
                "text": clean_pdf_text(page["text"]),       
            } 
            for page in pages
        ]

        source = PurePath(document).name
        
        author_pages = [0, 1, -1, -2] if len(pages_data) > 4 else [0, -1]
        author_mentioned_pages = " ".join(pages_data[page]["text"] for page in author_pages)

        author = extract_author(author_mentioned_pages)

        d_hash = get_doc_hash(document)

        data = {
            "payload": {
                "source": source,
                "author": author,
                "pages": pages_data,
                "doc_hash": d_hash,
            },
        }

        return data
    except Exception as e:
        print(e)
        raise

class Pipeline:
    def __init__(self, chunker, embedder, vector_db) -> None:
        self.chunker = chunker 
        self.embedder = embedder
        self.vector_db = vector_db 

    def process(self, data: List[Path]) -> None:
        for doc in data:
            try:
                normalized_data = data_normalize(doc)
                chunk_data = self.chunker.chunk(normalized_data)

                chunk_texts = [chunk_text for chunk_text, _ in chunk_data]
                vectors = self.embedder.embed(chunk_texts)

                ready_chunks = []
                for (chunk_text, chunk_meta), vector in zip(chunk_data, vectors):
                    unique_str = f"{chunk_meta['doc_hash']}_{chunk_text}"
                    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_str))

                    chunk = Chunk(text=chunk_text, vector=vector, payload=chunk_meta, id=uid)

                    ready_chunks.append(chunk)

                self.vector_db.upsert(ready_chunks)
            except Exception as e:
                print(e)
                raise


#sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng В ОБЯЗАТЕЛЬНОМ ПОРЯДКЕ, чтобы установился движок OCR занимающийся распознаванием трудного текста, таблиц и тд