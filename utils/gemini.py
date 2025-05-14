from google import genai
import os


def gemini_generate(prompt:str=None, file=None):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    if file is None:
        response = client.models.generate_content(
            model = 'gemini-2.0-flash-001',
            contents = prompt
        )
    else:
        file = client.files.upload(file=file)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[prompt, file]
        )
    return response.text