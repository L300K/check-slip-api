from dotenv import load_dotenv
from check_slip import checkSlip

if __name__ == '__main__':
    load_dotenv('.env.local')
    check_slip = checkSlip()
    # check_slip.captcha_solve()
    # print(check_slip.captcha_content)
    payload = check_slip.get_payload(slip_path='utils/IMG_1551.jpeg')
    print(check_slip.payload_content)