#! python


import argparse
import os
import subprocess

def convert_doc_to_pdf(doc_path, overwrite=False):
    file_name, file_extension = os.path.splitext(doc_path)
    pdf_path = f"{file_name}.pdf"
    exists_already = os.path.isfile(pdf_path)

    if exists_already:
        print(f"{pdf_path} is a file and it already exists!")
    else:
        print(f"{pdf_path} does not exist.")

    if overwrite or not exists_already:
        print(f"Writing {pdf_path}")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Word doc to PDF.")
    parser.add_argument("--file", required=True, help="Path to the Word document.")
    parser.add_argument("--overwrite", type=bool, default=False)

    args = parser.parse_args()
    word_file_path = args.file
    markdown_file_path = f"{word_file_path}.md"

    file_extension = os.path.splitext(word_file_path)[-1].lower()

    if file_extension == '.docx' or file_extension == '.doc':
        pdf_path = convert_doc_to_pdf(word_file_path, args.overwrite)
    else:
        print("Unsupported file format.")
        exit(1)
