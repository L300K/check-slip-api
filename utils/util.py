def sort_json(json_data):
    json_response_text = json_data.strip()
    if json_response_text.startswith("```json"):
        json_response_text = json_response_text[7:]
    if json_response_text.endswith("```"):
        json_response_text = json_response_text[:-3]
    sorted_data = json_response_text.strip()
    return sorted_data