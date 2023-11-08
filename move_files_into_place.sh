#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./move_files.sh <directory_to_process>"
    exit 1
fi

DIRECTORY="$1"

find raw -type f \( -name "*.markdown" \) -exec cp {} ./docs/_posts/ \;
find raw -type f \( -name "*.pdf" \) -exec cp {} ./docs/assets/pdf/ \;
find raw -type f \( -name "*.png" \) -exec cp {} ./docs/assets/img/posts/ \;
