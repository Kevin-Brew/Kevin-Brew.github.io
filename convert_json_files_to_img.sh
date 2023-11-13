#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./convert_files.sh <directory_to_process>"
    exit 1
fi

DIRECTORY="$1"

# Find .json files in the specified directory and execute the python script on each
find "$DIRECTORY" \( -name "*.json" \) | xargs -I {} python src/json_to_img.py --file {} --overwrite False

echo "Processing complete."
