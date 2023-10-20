#! python

import argparse
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import argparse
from docx import Document
import pdfplumber
import os
import subprocess
from PIL import Image
import pytesseract
import tempfile

def convert_doc_to_pdf(doc_path):
    file_name, file_extension = os.path.splitext(doc_path)
    pdf_path = f"{file_name}.pdf"
    subprocess.run([
        'soffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        os.path.dirname(doc_path),
        doc_path
    ])
    return pdf_path

def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def ocr_png_files(png_files):
    text = []
    for file_path in png_files:
        text.append(pytesseract.image_to_string(Image.open(file_path)))
    return "\n".join(text)

def write_to_markdown(content, output_file):
    with open(output_file, "w") as f:
        f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Word doc to PDF.")
    parser.add_argument("--file", required=True, help="Path to the Word document.")

    args = parser.parse_args()
    word_file_path = args.file
    markdown_file_path = f"{word_file_path}.md"

    file_extension = os.path.splitext(word_file_path)[-1].lower()

    if file_extension == '.docx' or file_extension == '.doc':
        pdf_path = convert_doc_to_pdf(word_file_path)
    else:
        print("Unsupported file format.")
        exit(1)
