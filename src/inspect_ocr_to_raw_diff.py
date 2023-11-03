#! python

import os
import json
import argparse


def load_json_files(directory):
    json_files_map = {}

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    try:
                        json_files_map[file_path] = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"Error loading JSON from {file_path}: {e}")
    return json_files_map


def main():
    parser = argparse.ArgumentParser(description="Recursively list and load JSON files in a directory.")
    parser.add_argument("--directory", required=True, help="Directory to search for JSON files")

    args = parser.parse_args()
    directory_path = args.directory
    json_files = load_json_files(directory_path)

    # Print the map (optional)
    for path, content in json_files.items():
        if 'raw_text' in content:
            n = len(content['raw_text'])
            o = len(content['request']['raw_ocr_content'])
            print(f"File: {path}, Original {o}, New {n}")
        else:
            print(f"File: {path}, Malformed")


if __name__ == "__main__":
    main()
