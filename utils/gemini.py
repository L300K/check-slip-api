from google import genai
import json
from PIL import Image
import os
from utils.util import sort_json

def gemini_generate(prompt: str = None, file=None):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    if file is None:
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt
        )
    elif file is not None:
        img = Image.open(file)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[prompt, img]
        )
        result_json = json.loads(sort_json(response.text))
        return result_json
    else:
        file = client.files.upload(file=file)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[prompt, file]
        )
    print(response.text)
    return response.text
