import json
from datetime import datetime

def read_json():
    try:
        with open("signals.json", mode='r', encoding="utf-8") as file:
            data = json.loads(file.read())
            return data
    except json.decoder.JSONDecodeError as err:
        print(f"Error decoding JSON: {err}")
        return []

def write_json(data):
    json_data = json.dumps(data, ensure_ascii=False)
    with open('signals.json', mode='w', encoding="utf-8") as file:
        file.write(json_data)

def clear_json():
    write_json([])

def convert_strdate_to_date(strdate):
    date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M")
    return date_object