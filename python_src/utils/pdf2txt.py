import re
from jieba.analyse import ChineseAnalyzer
from typing import BinaryIO

# import pypdf
import pdfquery

# def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
#     reader = pypdf.PdfReader(pdf_file)
#     for page in reader.pages:
#         print(page.extract_text().replace('\n', ''))
#     return ' '.join([
#         page.extract_text()
#         for page in reader.pages
#     ])

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
    