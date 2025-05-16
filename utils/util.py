from bs4 import BeautifulSoup


def sort_json(data_text):
    start_tag = "```json"
    end_tag = "```"
    start_index = data_text.find(start_tag)
    end_index = data_text.find(end_tag, start_index + len(start_tag))

    if start_index != -1 and end_index != -1:
        json_block = data_text[start_index + len(start_tag):end_index]
        return json_block.strip()
    else:
        return None


def extract_transaction_data(html_content):
    if "Transaction refunded" in html_content or "Slip not found" in html_content:
        return {
            "message": "Slip not found."
        }
    soup = BeautifulSoup(html_content, 'html.parser')

    output_data = {
        "message": None,
        "data": {
            "ref": None,
            "date": None,
            "amount": None,
            "sender_details": {
                "official_bank_name": None,
                "sender_name": None,
                "sender_id": None
            },
            "receiver_details": {
                "official_bank_name": None,
                "receiver_name": None,
                "receiver_id": None
            }
        }
    }

    def get_value_from_row(row, is_message_row=False):
        cells = row.find_all('td')
        if len(cells) == 2:
            if is_message_row:
                label_tag = cells[1].find('label')
                return label_tag.get_text(strip=True) if label_tag else cells[1].get_text(strip=True)
            return cells[1].get_text(strip=True)
        return None

    hid1_div = soup.find('div', id='hid1')
    if hid1_div:
        table_hid1 = hid1_div.find('table')
        if table_hid1:
            rows = table_hid1.find_all('tr')
            for row in rows:
                label_cell = row.find('td', class_='topic')
                if label_cell:
                    label_text = label_cell.get_text(strip=True)
                    if "ผลการค้นหา" in label_text or "Verification Status" in label_text:
                        output_data["message"] = get_value_from_row(row, is_message_row=True)
                    elif "เลขที่รายการ" in label_text or "Ref ID" in label_text:
                        output_data["data"]["ref"] = get_value_from_row(row)

    transaction_details_header = None
    for h6 in soup.find_all('h6'):
        if "รายละเอียดการทำรายการ / Transaction Details" in h6.get_text(strip=True):
            transaction_details_header = h6
            break

    details_table = None
    if transaction_details_header:
        current_sibling = transaction_details_header.find_next_sibling()
        while current_sibling:
            if current_sibling.name == 'div' and 'card' in current_sibling.get('class', []):
                details_div_hidden1 = current_sibling.find('div', id='hidden_1')
                if details_div_hidden1:
                    details_table = details_div_hidden1.find('table')
                break
            current_sibling = current_sibling.find_next_sibling()

    if details_table:
        rows = details_table.find_all('tr')
        for row in rows:
            label_cell = row.find('td', class_='topic')
            if label_cell:
                label_text_raw = label_cell.get_text(separator=" ", strip=True)
                value = get_value_from_row(row)
                if value is None: continue

                if "Transaction Date & Time" in label_text_raw:
                    output_data["data"]["date"] = value
                elif "<b>โอนจาก </b> / <b>From </b> :" in str(label_cell) or (
                        "โอนจาก" in label_text_raw and "From" in label_text_raw):
                    output_data["data"]["sender_details"]["official_bank_name"] = value
                elif "From Account Name" in label_text_raw or "ชื่อผู้ทำรายการ" in label_text_raw:
                    output_data["data"]["sender_details"]["sender_name"] = value
                elif "From Account Number" in label_text_raw or "เลขที่บัญชีผู้ทำรายการ" in label_text_raw:
                    output_data["data"]["sender_details"]["sender_id"] = value
                elif "<b>ไปยัง </b> / <b>To </b> :" in str(label_cell) or (
                        "ไปยัง" in label_text_raw and "To" in label_text_raw):
                    output_data["data"]["receiver_details"]["official_bank_name"] = value
                elif "To Account Name" in label_text_raw or "Biller Name" in label_text_raw or "ชื่อผู้รับชำระ" in label_text_raw:
                    output_data["data"]["receiver_details"]["receiver_name"] = value
                elif "To PromptPay/Reference ID" in label_text_raw or \
                        "Biller ID / Account Number" in label_text_raw or \
                        "เลขที่ผู้รับชำระ" in label_text_raw:
                    output_data["data"]["receiver_details"]["receiver_id"] = value
                elif "Local Currency Amount" in label_text_raw:
                    output_data["data"]["amount"] = value
                elif ("Amount (THB)" in label_text_raw or \
                      "จำนวนเงิน (บาท)" in label_text_raw or \
                      ("Amount" in label_text_raw and "Local Currency Amount" not in label_text_raw)) and \
                        output_data["data"]["amount"] is None:
                    if "บาท /" in value and "THB" in value.upper():
                        parts = value.split('/')
                        potential_thb_part = parts[-1].strip()
                        if "THB" in potential_thb_part.upper():
                            output_data["data"]["amount"] = potential_thb_part
                    elif "THB" in value.upper():
                        output_data["data"]["amount"] = value
                    else:
                        try:
                            float(value)
                            if "THB" in label_text_raw.upper() or "บาท" in label_text_raw:
                                output_data["data"]["amount"] = f"{value} THB"
                            else:
                                output_data["data"]["amount"] = value
                        except ValueError:
                            output_data["data"]["amount"] = value

    return output_data
