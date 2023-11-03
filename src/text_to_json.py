#! python

import argparse
import os
from json import JSONDecodeError

import openai
import json

system_prompt = """
The user will give a json_blob that follows this schema. 
The name of the person providing the sermons is Kevin
{
  "file_name": {
    "type": "string",
    "description": "this is the file path to the file containing the sermons text, 
    often hints to the date of the sermons is in this file name, 
    e.g. 
     - Easter_Day - 2009, the date that easter day fell on in 2009
     - advent22015 which would be the 2nd sunday in advert in 2015
     - 1994-08-30 the date was explicit in the filename "
    }
  "raw_ocr_content": {
     "type": "string",
     "description": "This is raw OCR content of the sermons. 
     It may contain additional artifacts that make the text unclean. 
     A/ It may have page headers, such as the title of the sermons and 
     pages numbers e.g. 1 of 2. These will break the flow of the main text. 
     You should try to remove these when you process. 
     B/ It may contain handwritten notes (that have become text), 
     these wont fit into the flow of the text, and you your try to remove 
     these when you process.  
     C/ It may have errors such as 
        - D's become G's, e.g. Days became Gays
        - l becomes an i, e.g will became wiii
        - d becomes a c
        - u becomes w
        " 
  }
}

You will call the function send_sermon_details based on the users input.

"""


openai.api_key = os.getenv("OPENAI_API_KEY")


def load_file_to_string(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def get_processed_data(file_name):
    user = {"file_name" : file_name,
            "raw_ocr_content": load_file_to_string(file_name)}
    json_str = json.dumps(user, indent=4)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
              "role": "system",
              "content": system_prompt
            },
            {
              "role": "user",
              "content": json_str
            }
          ],
        functions = [
            {
              "name": "send_sermon_details",
              "description": "send processed and cleaned sermons details for publishing",
              "parameters": {
                "type": "object",
                "properties": {
                  "title": {
                    "type": "string",
                    "description": "A short 3-4 word catchy title for the sermons"
                  },
                  "date": {
                    "type": "string",
                    "description": "A date in the format YYYY-MM-DD that you have"
                                   "inferred from the filename and the raw_ocr_content. "
                                   "typically sermons happen on a Sunday. "
                                   "and will reference key time periods in the anglican "
                                   "calendar such as the second sunday of advent"
                  },
                  "blurb": {
                        "type": "string",
                        "description": "A short 3-4 sentence summary of the core message/teaching of the sermons."
                    },
                  "raw_text": {
                        "type": "string",
                        "description": "the text from raw_ocr_content cleaned up, "
                                       "1/ Remove page header information and page numberings. "
                                       "2/ keep the main text and only make minor coorections fixing "
                                       "the typos and correct where the OCR has garbled the letters. "
                                       "3/ allign the text using markdown to create clear pargraphs"
                                       "4/ where possible if other people are being quoted, try to pull this out in markdown block format"
                    }
                }
              }
            }
          ],
        temperature=0.31,
        max_tokens=5143,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        json_object = json.loads(str(response['choices'][0]['message']['function_call']['arguments']))
        json_object["request"] = user
        return json_object
    except JSONDecodeError as e:
        print(str(response))
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to post.")
    parser.add_argument("--file", required=True, help="Path to the text document.")
    parser.add_argument("--overwrite", type=bool, default=False)

    args = parser.parse_args()
    file_path = args.file
    overwrite = args.overwrite

    file_name, file_extension = os.path.splitext(file_path)

    if file_extension == '.txt':
        out_path = f"{file_name}.json"
        exists_already = os.path.isfile(out_path)
        if exists_already:
            print(f"{out_path} is a file and it already exists!")
        else:
            print(f"{out_path} does not exist.")

        if overwrite or not exists_already:
            print(f"Writing {out_path}")
            raw_data = get_processed_data(file_path)
            with open(out_path, 'w') as file:
                json.dump(raw_data, file, indent=4)
    else:
        print("Unsupported file format {}".format(file_path))
        exit(1)