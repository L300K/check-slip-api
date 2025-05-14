import os

import requests
import re
from utils.gemini import gemini_generate

class checkSlip:
    def __init__(self):
        self.session = requests.Session()
        self.captcha_path = None
        self.captcha_content = None

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