import os

import requests
import re
from utils.gemini import gemini_generate
import json

class checkSlip:
    def __init__(self):
        self.session = requests.Session()
        self.captcha_path = None
        self.captcha_content = None
        self.banks_path = f'utils/banks.json'
        self.payload_content = None

    def get_captcha(self):
        self.session.get('https://checkslip.scb.co.th/web/main')
        response = self.session.get('https://checkslip.scb.co.th/web/service/captcha.php')
        try:
            php_sess_id = re.search(r'PHPSESSID=([^;]+)', response.headers.get('Set-Cookie', ''))
            if php_sess_id:
                php_sess_id = php_sess_id.group(1)
                filename = f'utils/captcha/{php_sess_id}.png'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                self.captcha_path = filename
                return True
            else:
                raise Exception('Failed to get PHPSESSID')
        except Exception as e:
            print("error: ", e)
            return False

    def captcha_solve(self):
        captcha = self.get_captcha()
        if captcha:
            self.captcha_content = gemini_generate(prompt=os.getenv("CAPTCHA_PROMPT"),file=self.captcha_path)

    def get_payload(self, slip_path: str = None):
        try:
            with open(self.banks_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            bank_data_json_string = json.dumps(bank_data, indent=2)
            prompt = os.getenv("PAYLOAD_PROMPT").format(bank_data_json_string=bank_data_json_string)
            self.payload_content = gemini_generate(prompt=prompt, file=slip_path)
        except Exception as e:
            print("error: ", e)