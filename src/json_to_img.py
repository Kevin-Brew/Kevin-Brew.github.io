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
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    data = requests.get(image_url)
    with open(outpath, "wb") as file:
        file.write(data.content)


def getDALLEPrompt(json_object) -> str:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI

    text = json_object['raw_text']

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "Given a user context which will be a sermon or speech, call the create_dalle_prompt function. The function takes 4 paramters. Extract up to the top 3 main concepts from the user context. In the first parameter main_concepts send a map of concept_title mapped to a concept_summary of how the concept is discussed in the user context. " +
                "In the second parameter selected_concept send which of the main concepts could best best used to create a non religous pencil drawing that does not depict scenes of war or conflict." +
                "In the third paramter rational_for_selection provide the reason why you chose that concept." 
                "In the forth parameter image_prompt using the selected concept one detailed prompt that can then be send to DALLE-3 to create a non religous pencil diagram that contains no text image for that selected concept. Do not create prompts that will generate images depicting scenes of war or conflict due to content policy restrictions."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        functions=[
            {
                "name": "create_dalle_prompt",
                "description": "send enumerated core lessons, rational for selection, and dalle3 prompt to",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "main_concepts": {
                            "type": "object",
                            "description": "the top 4 concepts the sermon",
                            "additionalProperties": {
                                "type": "string"
                              }
                        },
                        "selected_concept": {
                            "type": "string",
                            "description": "the key of the main_concept selected to be turned into a image prompt"
                        },
                        "rational_for_selection": {
                            "type": "string",
                            "description": "why the concept was chosen to create a image prompt"
                        },
                        "image_prompt": {
                            "type": "string",
                            "description": "why the concept was chosen to create a image prompt"
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
        print(json.dumps(json_object, indent=4))
        return json_object
    except JSONDecodeError as e:
        print(str(response))
        json_object = {}
        json_object["base"] = str(response.choices[0].message.function_call.arguments)
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

            prompt = getDALLEPrompt(json_object)
            head_data = merge(json_object, prompt)

            # write the meta data
            with open(json_file_path, 'w') as file:
                json.dump(head_data, file, indent=4)

            create_image(prompt["image_prompt"], out_path)

    else:
        print("Unsupported file format.")
        exit(1)
