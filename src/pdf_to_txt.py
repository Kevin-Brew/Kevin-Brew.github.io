#! python

import argparse
import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import numpy as np
import cv2
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/anthonybrew/Development/Personal/Kevin-Brew.github.io/project_key.json"

def google_vision(image) -> str:
    open_cv_image = np.array(image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    roi = open_cv_image
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    success, encoded_image = cv2.imencode('.jpg', roi)
    roi_image = encoded_image.tobytes()
    roi_image = vision.Image(content=roi_image)

    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=roi_image)
    return response.text_annotations[0].description

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
            # t1 = pytesseract.image_to_string(image, config='--psm 1 -l ENG')
            t1 = google_vision(image)
            text.append(t1)

    return "\n".join(text)

def write_to_txt(content, output_file):
    with open(output_file, "w") as f:
        f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to text.")
    parser.add_argument("--file", required=True, help="Path to the PDF file.")
    parser.add_argument("--overwrite", type=bool, default=False)

    args = parser.parse_args()
    overwrite = args.overwrite
    pdf_file_path = args.file
    markdown_file_path = f"{pdf_file_path}.md"

    file_name, file_extension = os.path.splitext(pdf_file_path)

    if file_extension.lower() == '.pdf':
        out_path = f"{file_name}.txt"
        exists_already = os.path.isfile(out_path)
        if exists_already:
            print(f"{out_path} is a file and it already exists!")
        else:
            print(f"{out_path} does not exist.")

        if overwrite or not exists_already:
            print(f"Writing {out_path}")
            content = extract_text_from_pdf(pdf_file_path)
            write_to_txt(content, out_path)
    else:
        print("Unsupported file format.")
        exit(1)
