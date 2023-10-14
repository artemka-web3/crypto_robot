import json
from datetime import datetime
import aiofiles

async def read_signals():
    try:
        async with aiofiles.open("signals.json", mode='r', encoding="utf-8") as file:
            data = json.loads(await file.read())
            return data
    except json.decoder.JSONDecodeError as err:
        print(f"Error decoding JSON: {err}")
        return []

async def write_signals(data):
    json_data = json.dumps(data, ensure_ascii=False)
    async with aiofiles.open('signals.json', mode='w', encoding="utf-8") as file:
        await file.write(json_data)

async def clear_signals():
    await write_signals([])

async def convert_strdate_to_date(strdate):
    date_object = datetime.strptime(strdate, "%Y-%m-%d %H:%M")
    return date_object

async def get_users():
    async with aiofiles.open("users.json", mode='r', encoding="utf-8") as file:
        json_data = await file.read()
        data = json.loads(json_data)
        return data

async def add_users(data):
    json_data = json.dumps(data, ensure_ascii=False)
    async with aiofiles.open('users.json', mode='w', encoding="utf-8") as file:
        await file.write(json_data)

async def read_last_signal_dir():
    try:
        with aiofiles.open("last_signal_dir.json", mode='r', encoding="utf-8") as file:
            data = json.loads(await file.read())
            return data
    except json.decoder.JSONDecodeError as err:
        print(f"Error decoding JSON: {err}")
        return []

async def write_last_signal_dir(data):
    json_data = json.dumps(data, ensure_ascii=False)
    with aiofiles.open('last_signal_dir.json', mode='w', encoding="utf-8") as file:
        await file.write(json_data)

async def fullfill(symbols):
    data = {}
    for sym in symbols:
        data[sym] = '0'
    await write_last_signal_dir(data)