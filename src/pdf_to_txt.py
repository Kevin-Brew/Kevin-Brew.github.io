#! python


import argparse
import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # If pdfplumber cannot extract text, it's likely a scanned page
            if not page.extract_text():
                # Convert PDF page to image
                images = convert_from_path(pdf_path, first_page=page.page_number, last_page=page.page_number)
                for image in images:
                    text.append(pytesseract.image_to_string(image))
            else:
            # If it's not scanned, use pdfplumber's text extraction
                 text.append(page.extract_text())
    if len(text) == 0:
        # pdf plumber has failed lets do a raw extract
        images = convert_from_path(pdf_path)
        for image in images:
            text.append(pytesseract.image_to_string(image))

    return "\n".join(text)

def write_to_markdown(content, output_file):
    with open(output_file, "w") as f:
        f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to text.")
    parser.add_argument("--file", required=True, help="Path to the PDF file.")

    args = parser.parse_args()
    pdf_file_path = args.file
    markdown_file_path = f"{pdf_file_path}.md"

    file_name, file_extension = os.path.splitext(pdf_file_path)

    if file_extension.lower() == '.pdf':
        content = extract_text_from_pdf(pdf_file_path)
        write_to_markdown(content, f"{file_name}.md")
    else:
        print("Unsupported file format.")
        exit(1)
