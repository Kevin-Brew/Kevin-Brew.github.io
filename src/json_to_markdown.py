#! python

import argparse
import json
import os

def get_filename_without_extension(path):
    base_name = os.path.basename(path)  # Get the filename with extension
    file_name_without_extension = os.path.splitext(base_name)[0]  # Split filename and extension
    return file_name_without_extension

def create_markdown(json_object):
    ans = """---
layout: post
title:  "{}"
date:   {}
blurb: "{}"
---
[Original PDF](/assets/pdf/{}.pdf)    
{}
""".format(
        json_object["title"],
        json_object["date"],
        json_object["blurb"],
        get_filename_without_extension(json_object["request"]["file_name"]),
        json_object["raw_text"]
    )
    return ans


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert json to markdown post.")
    parser.add_argument("--file", required=True, help="Path to the json file.")
    parser.add_argument("--overwrite", type=bool, default=False)

    args = parser.parse_args()

    json_file_path = args.file
    overwrite = args.overwrite

    file_name, file_extension = os.path.splitext(json_file_path)

    if file_extension.lower() == '.json':
        with open(json_file_path, 'r') as file:
            json_object = json.load(file)

        name = get_filename_without_extension(json_file_path)
        date = json_object['date']
        dir = os.path.dirname(json_file_path)

        out_path = f"{dir}/{date}-{name}.markdown"

        exists_already = os.path.isfile(out_path)
        if exists_already:
            print(f"{out_path} is a file and it already exists!")
        else:
            print(f"{out_path} does not exist.")

        if overwrite or not exists_already:
            print(f"---> Writing {out_path}")
            content = create_markdown(json_object)
            with open(out_path, 'w') as file:
                file.write(content)
    else:
        print("Unsupported file format.")
        exit(1)
