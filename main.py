from dotenv import load_dotenv
from check_slip import checkSlip

if __name__ == '__main__':
    load_dotenv('.env.local')
    check_slip = checkSlip()
    check_slip.captcha_solve()
    print(check_slip.captcha_content)