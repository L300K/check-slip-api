from dotenv import load_dotenv
from check_slip import checkSlip
import json
import time

if __name__ == '__main__':
    start_time = time.time()

    load_dotenv('.env.local')
    check_slip = checkSlip()
    check_slip.get_slip_data(slip_path='IMG_1559.JPG', max_retries=2)
    print(f'slip_data: {json.dumps(check_slip.slip_data, indent=4, ensure_ascii=False)}')

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.2f} seconds')
