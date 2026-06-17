from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode, TesseractOcrOptions
from rag_wv import RecursiveSplitter
import os
import time

os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata/"

pdf_pipeline_options = PdfPipelineOptions(do_table_structure=True, do_ocr=True)
pdf_pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pdf_pipeline_options.ocr_options = TesseractOcrOptions(lang=["rus", "eng"])


doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_pipeline_options),
    }
)

class DocHandler():
    def __init__(self):
        self.converter: DocumentConverter = doc_converter
    def convert(self, doc: str):
        return self.converter.convert(source=doc)

rs = RecursiveSplitter()
dh = DocHandler()

text = dh.convert("/home/warden/rag/documents/stocks.csv").document.export_to_markdown()

chunks = rs._splitter.split_text(text)

for c in chunks:
    print(c)
    time.sleep(10)    