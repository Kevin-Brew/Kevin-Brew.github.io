#!/bin/bash

# Check if an argument was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/directory"
    exit 1
fi

# The first argument is the directory path
directory="$1"

# Find all .txt files and check for corresponding .json files
find "$directory" -type f -name "*.txt" | while read txtfile; do
    jsonfile="${txtfile%.txt}.json"
    if [ ! -f "$jsonfile" ]; then
        echo "Missing JSON for: $txtfile"
    fi
done
