import json
from datetime import datetime, timedelta


def read_last_signal_dir():
    try:
        with open("last_signal_dir.json", mode='r', encoding="utf-8") as file:
            data = json.loads(file.read())
            return data
    except json.decoder.JSONDecodeError as err:
        print(f"Error decoding JSON: {err}")
        return []

def write_last_signal_dir(data):
    json_data = json.dumps(data, ensure_ascii=False)
    with open('last_signal_dir.json', mode='w', encoding="utf-8") as file:
        file.write(json_data)

def fullfill(symbols):
    data = {}
    for sym in symbols:
        data[sym] = {'last_signal':  "0", "last_time": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')}
    write_last_signal_dir(data)



def convert_strdate_to_date(strdate):
    date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M")
    return date_object

