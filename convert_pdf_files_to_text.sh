#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./convert_files.sh <directory_to_process>"
    exit 1
fi

DIRECTORY="$1"

# Find .doc and .docx files in the specified directory and execute the python script on each
find "$DIRECTORY" \( -name "*.pdf" \) | xargs -I {} python src/pdf_to_txt.py --file {}

echo "Processing complete."
