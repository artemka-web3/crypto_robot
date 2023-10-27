import aiofiles
import json
import ccxt
from combo import get_historical_data
from datetime import datetime
import pygsheets
import traceback


gc = pygsheets.authorize(service_account_file='sheets_key.json')
ws = gc.open('Крипта стата').worksheet()

COLS_TO_UPDATE = ["I", 'J', 'K']

# Define color constants
RED_BACKGROUND = (1, 0.8, 0.8)
GREEN_BACKGROUND = (0.8, 1, 0.8)
YELLOW_BACKGROUND = (1, 1, 0.8)


bitget = ccxt.binance()

async def upload_queue():
    tickers = ws.get_col(1)
    for n,i in enumerate(tickers):
        if i == '':
            tickers = tickers[:n]
            break
    rows_count = len(tickers)
    data = []
    async with aiofiles.open('analytics_queue.json', 'r', encoding='utf-8') as fp:
        data = json.loads(await fp.read())
    async with aiofiles.open('analytics_queue.json', 'w', encoding='utf-8') as fp:
        await fp.write('[]')
    for i in data:
        ws.update_row(rows_count+1, list(map(str, [i['ticker'], i['signal_type'], i['price'], i['take_profit'], i['stop_loss'], i['time'], str(i['take_perc']).replace('.', ','), str(i['stop_perc']).replace('.', ',')])))
        rows_count += 1


async def add_item_to_queue(ticker, price, take_profit, stop_loss, time, take_perc, stop_perc, signal_type):
    data = []
    async with aiofiles.open('analytics_queue.json', 'r', encoding='utf-8') as fp:
        data = json.loads(await fp.read())
    data.append({
        'ticker': ticker,
        'price': price,
        'take_profit': take_profit,
        'stop_loss': stop_loss,
        'time': time,
        'take_perc': take_perc,
        'stop_perc': stop_perc,
        'signal_type': signal_type
    })
    async with aiofiles.open('analytics_queue.json', 'w', encoding='utf-8') as fp:
        await fp.write(json.dumps(data, ensure_ascii=False))

async def update_sheet():
    try: await upload_queue()
    except Exception as e: print(e)
    try:
        # Open Google Sheets and get data
        print('Processing signals')
        data = ws.get_all_values(returnas='matrix')

        # Skip the header
        data = data[1:]

        # Get column indices
        ticker_idx = 0
        signal_type_idx = 1
        take_profit_idx = 3
        stop_loss_idx = 4
        time_idx = 5
        result_idx = 8
        time_result_idx = 9
        deadline_idx = 10

        for row in data:
            ticker = row[ticker_idx]
            if ticker == '':
                print('Processing signals finished')
                break
            signal_type = row[signal_type_idx]
            take_profit = float(row[take_profit_idx])
            stop_loss = float(row[stop_loss_idx])
            result = str(row[result_idx])
            entry_time = datetime.strptime(row[time_idx], "%Y-%m-%d %H:%M")
            current_time = datetime.now()

            historical_data = get_historical_data(ticker, '4h', 200, bitget)
            entry_price = historical_data['close'].iloc[-1]

            background_color = None

            if result not in ["Выбито по стоп лоссу", "Сделка сработана успешно"]:
                if signal_type == '🔴 SHORT':
                    if entry_price >= stop_loss:
                        row[result_idx] = 'Выбито по стоп лоссу'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = RED_BACKGROUND
                    elif entry_price <= take_profit:
                        row[result_idx] = 'Сделка сработана успешно'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = GREEN_BACKGROUND
                    else:
                        row[result_idx] = 'Ожидание'
                        background_color = YELLOW_BACKGROUND
                elif signal_type == '🟢 LONG':
                    if entry_price <= stop_loss:
                        row[result_idx] = 'Выбито по стоп лоссу'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = RED_BACKGROUND
                    elif entry_price >= take_profit:
                        row[result_idx] = 'Сделка сработана успешно'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = GREEN_BACKGROUND
                    else:
                        row[result_idx] = 'Ожидание'
                        background_color = YELLOW_BACKGROUND

            set_cell_colors(background_color, data, row)

        ws.update_values(crange=(2, 1), values=data)
    except Exception as e:
        print(traceback.format_exc())
def set_cell_colors(background_color, data, row):
    if background_color:
        for col in COLS_TO_UPDATE:
            cell = ws.cell(f'{col}{data.index(row) + 2}')
            cell.color = background_color
            cell.update()
