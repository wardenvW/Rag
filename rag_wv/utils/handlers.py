import logging
import re
import pymupdf4llm
from typing import Callable
from ..config import ALLOWED_FILE_EXTENSIONS

logger = logging.getLogger(__name__)

def clean_pdf_text(text: str) -> str:
    text = re.sub(r"==> picture \[\d+ x \d+\] <==", "\n[ИЗОБРАЖЕНИЕ]\n", text)

    text = re.sub(r"----- Start of picture text -----", "", text)
    text = re.sub(r"----- End of picture text -----", "", text)

    text = re.sub(r"<br>", "", text)
    
    return text.strip()


def pdf_handler(document) -> str:
    pages = pymupdf4llm.to_text(document, ocr_language = "rus+eng", page_chunks = True)
    pages_data = [
        {
            "page": page["metadata"]["page_number"], 
            "text": clean_pdf_text(page["text"]),       
        } 
        for page in pages
    ]
    return pages_data

    #TODO: Реализовать также обработку картинок и тд

def doc_handler(document) -> str:
    pass

def docx_handler(document) -> str:
    pass

def txt_handler(document) -> str:
    pass

"""
Не забывать менять список разрешённых расширений в config.py
"""
document_handlers: dict[str, Callable] = {
    ".pdf": pdf_handler,
    ".doc": doc_handler,
    ".docx": docx_handler,
    ".txt": txt_handler,
}
   


def get_handler(extension: str) -> Callable:
    return document_handlers[extension]