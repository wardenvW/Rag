import re
import pymupdf4llm
from typing import List, Dict, Any
from hashlib import file_digest
from pathlib import PurePath

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