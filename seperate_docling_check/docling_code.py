from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter,PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions
)


import time 
import requests
from pathlib import Path 
from IPython.display import display
import pandas as pd 
import matplotlib.pyplot as plt
import math 
import os

os.environ['NO_PROXY'] = 'localhost,127.0.0.1,huggingface.co'


# Configure OCR pipeline
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True  # Enable OCR
pipeline_options.ocr_options = TesseractOcrOptions()  # Use Tesseract OCR

# For Japanese text, configure language support
# pipeline_options.ocr_options = TesseractOcrOptions(lang="jpn+eng")  # Uncomment for Japanese

# Create converter with OCR enabled
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

start_time = time.time()
source = "test_pdf.pdf"
converter = DocumentConverter()
result = converter.convert(source)

end_time = time.time() - start_time

print(f"Total time take for parsing {end_time:.2f} seconds.")
print(result.document.export_to_markdown())