import logging
import re
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode, TesseractOcrOptions
from typing import Callable
from langchain_core.documents import Document
from ..models import PageSpan
from .preprocessing import data_normalize
from typing import List, Dict, Any
from pathlib import Path

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

def clean_pdf_text(text: str) -> str:
    text = re.sub(r"==> picture \[\d+ x \d+\] <==", "\n[ИЗОБРАЖЕНИЕ]\n", text)

    text = re.sub(r"----- Start of picture text -----", "", text)
    text = re.sub(r"----- End of picture text -----", "", text)

    text = re.sub(r"<br>", "", text)
    
    return text.strip()

os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata/"

pdf_pipeline_options = PdfPipelineOptions(do_table_structure=True, do_ocr=True)
pdf_pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pdf_pipeline_options.ocr_options = TesseractOcrOptions(lang=["rus", "eng"])


doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_pipeline_options),
    }
)

def pdf_handler(document: Path, d_type: str, splitter: RecursiveCharacterTextSplitter) -> list:
    data = data_normalize(document, d_type, extract_author_flag=True)

    pages_data = [
        {
            "page": page["metadata"]["page_number"], 
            "text": clean_pdf_text(page["text"]),       
        } 
        for page in data["payload"]["pages"]
    ]

    results = []
    full_text = " ".join(page["text"] for page in pages_data) + " "
    
    payload = data.get("payload")

    doc = Document(
        page_content=full_text,
        metadata={
            "source": payload.get("source", "Unknown"),
            "author": payload.get("author", "Unknown"),
            "doc_hash": payload.get("doc_hash"),
            "type": payload.get("type", "Unknown"),
        }
    )
    logger.info("Creating page mapping")
    map_list = create_page_mapping(pages_data)
    logger.info("Created")

    logger.info("Document splitting")
    chunks = splitter.split_documents([doc])
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

def universal_handler(document: Path, d_type: str, splitter: RecursiveCharacterTextSplitter) -> list:
    data = data_normalize(document, d_type)
    payload = data.get("payload")
    text = doc_converter.convert(document).document.export_to_text()

    doc = Document(
        page_content= text,
        metadata={
            "source": payload.get("source", "Unknown"),
            "author": payload.get("author", "Unknown"),
            "doc_hash": payload.get("doc_hash"),
            "type": payload.get("type", "Unknown"),
        }
    )

    chunks = splitter.split_documents([doc])
    results = []

    for c in chunks:
        results.append(
            (
                c.page_content,
                {
                    "page": "Unknown",
                    **c.metadata
                }
            )
        )
    
    return results


"""
Не забывать менять список разрешённых расширений в config.py
"""
document_handlers: dict[str, Callable] = {
    ".pdf": pdf_handler,
    ".doc": universal_handler,
    ".docx": universal_handler,
    ".csv": universal_handler,
    ".xlsx": universal_handler,
    ".txt": universal_handler,
}
   


def get_handler(extension: str) -> Callable:
    return document_handlers[extension]


