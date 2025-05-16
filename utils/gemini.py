from google import genai
from PIL import Image
import os
import time
from utils.util import sort_json

def gemini_generate(prompt: str = None, file=None, captcha=None, max_retries=5, backoff_factor=2):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = 'gemini-2.0-flash'
    retries = 0
    while retries <= max_retries:
        try:
            if file is None:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
            elif captcha is None and file is not None:
                img = Image.open(file)
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, img]
                )
                result_json = sort_json(response.text)
                return result_json
            else:
                file = client.files.upload(file=file)
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, file]
                )
            return response.text

        except Exception as e:
            if '503' in str(e) or 'UNAVAILABLE' in str(e):
                wait_time = backoff_factor ** retries
                print(f"Model overloaded (503), retrying in {wait_time} seconds... (Attempt {retries + 1})")
                time.sleep(wait_time)
                retries += 1
            else:
                raise

    raise RuntimeError("Max retries exceeded due to repeated 503 ServerError.")
