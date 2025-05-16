import json
import os

import requests

from utils.gemini import gemini_generate
from utils.util import extract_transaction_data


class checkSlip:
    def __init__(self):
        self.captcha_path = None
        self.captcha_content = None
        self.banks_path = f'utils/banks.json'
        self.payload_content = None
        self.php_sess_id = None
        self.ts = None
        self.slip_data = None
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://checkslip.scb.co.th/web/main',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        }

    def get_captcha(self):
        response = requests.get('https://checkslip.scb.co.th/web/main', headers=self.headers)
        self.ts = requests.utils.dict_from_cookiejar(response.cookies)['TS010b4e86']
        cookies = {
            'TS010b4e86': self.ts
        }
        response = requests.get('https://checkslip.scb.co.th/web/service/captcha.php', cookies=cookies)
        self.ts = requests.utils.dict_from_cookiejar(response.cookies)['TS010b4e86']
        self.php_sess_id = requests.utils.dict_from_cookiejar(response.cookies)['PHPSESSID']
        try:
            if self.php_sess_id:
                filename = f'utils/captcha/{self.php_sess_id}.png'
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
            self.captcha_content = gemini_generate(prompt=os.getenv("CAPTCHA_PROMPT"), file=self.captcha_path,
                                                   captcha=True)
            print('Captcha resolved successfully.')

    def get_payload(self, slip_path: str = None):
        try:
            with open(self.banks_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            bank_data_json_string = json.dumps(bank_data, indent=2)
            prompt = os.getenv("PAYLOAD_PROMPT").format(bank_data_json_string=bank_data_json_string)
            self.payload_content = json.loads(gemini_generate(prompt=prompt, file=slip_path))
            return True
        except Exception as e:
            print("error: ", e)
            return False

    def get_slip_data(self, max_retries: int, slip_path: str = None):
        retries = 0
        captcha_invalid_once = False

        while retries < max_retries:
            if not captcha_invalid_once:
                self.captcha_solve()

            self.get_payload(slip_path)
            data = {
                'tran': self.payload_content['transaction_ref_code'],
                'bank': self.payload_content['thai_bank_code'],
                'amount': self.payload_content['amount'],
                'captcha_input': str(self.captcha_content),
            }

            print("data: ", data)

            cookies = {
                'TS010b4e86': self.ts,
                'PHPSESSID': self.php_sess_id
            }

            response = requests.post(
                'https://checkslip.scb.co.th/web/main',
                cookies=cookies,
                data=data,
                headers=self.headers
            )

            system_err = "System is unavailable. Please try again"
            invalid_captcha = "Invalid captcha code"

            check_system_error = sorted(
                system_err.lower().replace('.', '').split()) if system_err in response.text else []
            check_invalid_captcha = sorted(
                invalid_captcha.lower().replace('.', '').split()) if invalid_captcha in response.text else []

            if check_system_error:
                print("System error occurred.")
                self.slip_data = None
                return self.slip_data

            elif check_invalid_captcha:
                if not captcha_invalid_once:
                    self.captcha_solve()
                    captcha_invalid_once = True
                    print("Invalid captcha code. Retrying...")
                else:
                    print("Already retried with captcha solve. Skipping additional solve.")
                continue

            else:
                print("Slip data retrieved. Checking content...")
                self.slip_data = extract_transaction_data(response.text)
                if (
                        isinstance(self.slip_data, dict) and
                        'data' in self.slip_data and
                        'amount' in self.slip_data['data'] and
                        self.slip_data['data']['amount']
                ):
                    print("Valid slip data with amount found.")
                    return self.slip_data
                else:
                    print("Amount is missing or data structure is invalid. Retrying...")
                    captcha_invalid_once = False
            retries += 1

        print(f"Max retries ({max_retries}) reached.")
        return self.slip_data

