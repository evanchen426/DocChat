from typing import BinaryIO

import pypdf

def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
    reader = pypdf.PdfReader(pdf_file)
    return '\n'.join([
        page.extract_text()
        for page in reader.pages
    ])
    