#! python
from json import JSONDecodeError

from openai import OpenAI
import argparse
import os, json
import requests
from jsonmerge import merge

from json_to_markdown import get_filename_without_extension
client = OpenAI()


def create_image(prompt, outpath):
    response = client.images.generate(
        model="dall-e-3",
        prompt="An uplifting simple pencil line drawing of a single concept that " +
               "represents the main message from the following sermon:" +
               prompt,
        size="1024x1024",
        quality="hd",
        n=1,
        style="vivid"
    )
    image_url = response.data[0].url
    data = requests.get(image_url)
    with open(outpath, "wb") as file:
        file.write(data.content)


def getSummaryAndRational(json_object) -> str:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI

    text = json_object['raw_text']

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "user",
                "content": "I want you to extract the top 4 concepts from a sermon I will paste. I want you to then select the concept that you best think can be graphically represented as non religious black and white pencil digram no text only images. Create one detailed prompt that can then be used in DALLE-3 to create an image for that concept.\n\nYou will not be able to generate images depicting scenes of war or conflict due to content policy restrictions.\n"
            },
            {
                "role": "assistant",
                "content": "Please paste the sermon text here, and I'll analyze it to extract the top 4 concepts. Once we have those concepts, we can proceed to select one that is suitable for a non-religious graphical representation and create a detailed prompt for DALL-E 3."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.31,
        max_tokens=4096, #remaining_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    s = str(response.choices[0].message.content)
    return s


def getDALLEPrompt(text) -> str:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "From the provided summary and prompt provided from DALLE-3 extract the prompt without modification and pass it to the function generate"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        functions=[
            {
                "name": "generate",
                "description": "takes a dalle-3 prompt and generates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "the prompt to call dalle-3"
                        }
                    }
                }
            }
        ],
        temperature=0.01,
        max_tokens=1000, #remaining_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    s = str(response.choices[0].message.function_call.arguments)
    json_object = json.loads(s)
    json_object["summary"] = text
    print(json.dumps(json_object, indent=4))
    return json_object


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert json to prompt and image.")
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

        out_path = f"{dir}/{name}.png"

        exists_already = os.path.isfile(out_path)
        if exists_already:
            print(f"{out_path} is a file and it already exists!")
        else:
            print(f"{out_path} does not exist.")

        if overwrite or not exists_already:
            print(f"---> Writing {out_path}")

            s = getSummaryAndRational(json_object)
            prompt = getDALLEPrompt(s)
            head_data = merge(json_object, prompt)

            # write the meta data
            with open(json_file_path, 'w') as file:
                json.dump(head_data, file, indent=4)

            create_image(prompt["prompt"], out_path)

    else:
        print("Unsupported file format.")
        exit(1)
