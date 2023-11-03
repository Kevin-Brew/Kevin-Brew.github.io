#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./convert_files.sh <directory_to_process>"
    exit 1
fi

DIRECTORY="$1"
BATCH_SIZE=1 # Set the batch size

# Find .doc and .docx files in the specified directory and execute the python script on each
find "$DIRECTORY" \( -name "*.txt"  \) | xargs -P $BATCH_SIZE -I {} python src/text_to_json.py --file {}

echo "Processing complete."
