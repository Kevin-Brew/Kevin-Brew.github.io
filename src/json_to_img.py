#! python
from openai import OpenAI
import argparse
import os, json
import requests

from json_to_markdown import get_filename_without_extension
client = OpenAI()


def create_image(json_object, outpath):
    response = client.images.generate(
        model="dall-e-3",
        prompt="An uplifting simple pencil line drawing of a single concept that " +
               "represents the main message from the following sermon:" +
               json_object['blurb'],
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    data = requests.get(image_url)
    with open(outpath, "wb") as file:
        file.write(data.content)


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

        out_path = f"{dir}/{date}-{name}.png"

        exists_already = os.path.isfile(out_path)
        if exists_already:
            print(f"{out_path} is a file and it already exists!")
        else:
            print(f"{out_path} does not exist.")

        if overwrite or not exists_already:
            print(f"---> Writing {out_path}")
            create_image(json_object, out_path)

    else:
        print("Unsupported file format.")
        exit(1)
