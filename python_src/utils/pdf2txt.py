import re
from typing import BinaryIO

import pdfquery

def contain_chinese(s: str) -> bool:
    return re.match(r'\u4e00-\u9fff', s) is not None

def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
    pdf = pdfquery.PDFQuery(pdf_file)
    pdf.load()
    xml_tree = pdf.get_tree()
    text_lines = []
    for node in xml_tree.iter():
        if node.text is not None:
            text_lines.append(node.text)
    extracted_texts = '\n'.join(text_lines)
    # print(extracted_texts)
    return extracted_texts
    