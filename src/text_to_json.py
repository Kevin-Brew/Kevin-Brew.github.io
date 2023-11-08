#! python

import argparse
import os
from json import JSONDecodeError
import tiktoken
import json
from jsonmerge import merge

# This code is for v1 of the openai package: pypi.org/project/openai

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
gpt_encoder = None
function_count = 294
sys_count = None

def init():
    global gpt_encoder
    global sys_count
    gpt_encoder = tiktoken.encoding_for_model("gpt-4-1106-preview")
    sys_count = count_tokens(system_prompt)

def count_tokens(content: str) -> int:
    return len(gpt_encoder.encode(content))


def load_file_to_string(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def get_processed_data(file_name):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI

    user = {"file_name": file_name,
            "raw_ocr_content": load_file_to_string(file_name)}
    json_str = json.dumps(user, indent=4)

    user_count = count_tokens(json_str)
    remaining_tokens = 100000 - user_count - sys_count - function_count

    print("User {}, System {}, Function {}, Completion tokens {}".format(user_count,sys_count, function_count,remaining_tokens))

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
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
        functions=[
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
        max_tokens=4096, #remaining_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        s = str(response.choices[0].message.function_call.arguments)
        json_object = json.loads(s)
        json_object["request"] = user
        return json_object
    except JSONDecodeError as e:
        print(str(response))
        json_object = {}
        json_object["request"] = user
        json_object["base"] = str(response['choices'][0]['message']['function_call']['arguments'])
        return json_object


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
            init()
            print(f"Writing {out_path}")
            head_data = get_processed_data(file_path)
            if exists_already:
                with open(out_path) as file:
                    base_data = json.load(out_path)
                    head_data = merge(base_data, head_data)

            with open(out_path, 'w') as file:
                json.dump(head_data, file, indent=4)
    else:
        print("Unsupported file format {}".format(file_path))
        exit(1)
