from aiogram import Bot, Dispatcher, executor, types, exceptions
import aioschedule
import asyncio
import logging
import requests

from combo import combo_strategy_full, get_historical_data
from json_utils import *

from config import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    data = await get_users()
    in_db = False
    for i in data:
        if i['user_id'] == int(message.from_user.id):
            in_db = True
            break
    if not in_db:
        new_user = {"user_id": int(message.from_user.id)}
        data.append(new_user)
        await add_users(data)
        await message.answer('Добро пожаловать! Скоро вы будете получать сигналы по криптовалютам!')
    await message.answer('Этот бот отслеживает криптовалюты с биржи binance и отправляет сигналы на покупку/продажу')


async def clear_last_signal():
    await write_last_signal_dir({})
    symbols = []
    endpoint = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    headers = {
        'X-MBX-APIKEY': BINANCE_API_KEY
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        сounter = 0
        for symbol_info in data['symbols']:
            if 'BUSD' not in symbol_info['symbol']:
                symbols.append(symbol_info['symbol'])
            сounter += 1
    else:
        print('Failed to retrieve data from Binance API')
    await fullfill(symbols)

async def send():
    signals = await read_signals()
    users = await get_users()
    if signals:
        for item in signals:
            for user in users:
                try:
                    await bot.send_message(
                        int(user['user_id']),
                        f"<b>{item['signal_type']}</b> - #{item['ticker']}\n\n"+
                        f"✅<b>ЦЕНА ВХОДА:</b> ${round(item['price'], 2)}\n\n"+
                        f"💰<b>ТЕЙК-ПРОФИТ:</b>\n${item['take_profit']}\n\n"+
                        f"<b>🛑СТОП-ЛОСС:</b>\n${item['stop_loss']}\n\n"+
                        f"<b>🎯ЦЕЛЬ 1:</b>\n${item['fixations'][0]}\n\n"+
                        f"<b>🎯ЦЕЛЬ 2:</b>\n${item['fixations'][1]}\n\n"+
                        f"<b>🎯ЦЕЛЬ 3:</b>\n${item['fixations'][2]}\n\n"+
                        f"<b>🕒ВРЕМЯ СИГНАЛА:</b>\n{item['time']}\n_____\n\n"+

                        f"<b>ПОТЕНЦИАЛЬНАЯ ПРИБЫЛЬ:</b>\n{round(item['take_perc'], 4)}%\n\n"+
                        f"<b>ПОТЕНЦИАЛЬНЫЕ ПОТЕРИ:</b>\n{round(item['stop_perc'], 4)}%\n\n"+
                        "*<i>Сигнал замечен на тф 4 часа</i>",
                        disable_notification=False,
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except exceptions.RetryAfter as e:
                    asyncio.sleep(e.timeout)
                    logging.info(f'блокировка бота на {e.timeout}')
                except Exception as e:
                    logging.info(f"{item['ticker']}\nОшибка отправки\n", e)
                    continue
        clear_signals()

async def schedule_tasks():
    aioschedule.every(10).seconds.do(send)
    aioschedule.every(60).minutes.do(clear_last_signal)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    symbols = []
    endpoint = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    headers = {
        'X-MBX-APIKEY': BINANCE_API_KEY
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        сounter = 0
        for symbol_info in data['symbols']:
            if 'BUSD' not in symbol_info['symbol']:
                symbols.append(symbol_info['symbol'])
            сounter += 1
    else:
        print('Failed to retrieve data from Binance API')
    await fullfill(symbols)
    for s in symbols:
        asyncio.create_task(combo_strategy_full(s))
    asyncio.create_task(schedule_tasks())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)