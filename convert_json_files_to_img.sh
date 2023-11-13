#!/bin/bash

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: ./convert_files.sh <directory_to_process> [string_to_match]"
    exit 1
fi

DIRECTORY="$1"
STRING_TO_MATCH="$2"

# Function to process file
process_file() {
    python src/json_to_img.py --file "$1"
}

# Find .json files in the specified directory
# If STRING_TO_MATCH is provided, only process files containing the string
find "$DIRECTORY" -name "*.json" | while read -r file; do
    if [ -z "$STRING_TO_MATCH" ] || grep -q "$STRING_TO_MATCH" "$file"; then
        process_file "$file"
    fi
done

echo "Processing complete."
