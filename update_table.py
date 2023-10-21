import analytics
import aioschedule
import asyncio
import gspread_formatting as gsf
from signals_json import read_json
from combo import get_historical_data
from datetime import datetime, timedelta
import pygsheets
from config import bitget


# Define the column letters as constants
COLS_TO_UPDATE = ["I", 'J', 'K']

# Define color constants
RED_BACKGROUND = (1, 0.8, 0.8)
RED_TEXT = (0.4, 0, 0, 1.0)
GREEN_BACKGROUND = (0.8, 1, 0.8)
GREEN_TEXT = (0, 0.4, 0, 1.0)
YELLOW_BACKGROUND = (1, 1, 0.8)
YELLOW_TEXT = (0.4, 0.4, 0, 1.0)



async def update_analytics():
    try:
        # Open Google Sheets and get data
        print('Processing signals')
        data = analytics.ws.get_all_values(returnas='matrix')

        # Skip the header
        header = data[0]
        data = data[63:]

        # Get column indices
        ticker_idx = header.index('Тикер')
        signal_type_idx = header.index('Тип сигнала')
        take_profit_idx = header.index('Тейк профит')
        stop_loss_idx = header.index('Стоп лосс')
        time_idx = header.index('Время сигнала')
        result_idx = header.index('Результат')
        time_result_idx = header.index('Время достижения цели (дата+ часы:минуты) ')
        deadline_idx = header.index('Срок достижения результата')

        for row in data:
            ticker = row[ticker_idx]
            signal_type = row[signal_type_idx]
            take_profit = float(row[take_profit_idx])
            stop_loss = float(row[stop_loss_idx])
            result = str(row[result_idx])
            entry_time = datetime.strptime(row[time_idx], "%Y-%m-%d %H:%M")
            current_time = datetime.now()

            historical_data = get_historical_data(ticker, '4h', 200, bitget)
            entry_price = historical_data['close'].iloc[-1]

            background_color = None
            text_color = None

            if result not in ["Выбито по стоп лоссу", "Сделка сработана успешно"]:
                if signal_type == '🔴 SHORT':
                    if entry_price >= stop_loss:
                        row[result_idx] = 'Выбито по стоп лоссу'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = RED_BACKGROUND
                        text_color = RED_TEXT
                    elif entry_price <= take_profit:
                        row[result_idx] = 'Сделка сработана успешно'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = GREEN_BACKGROUND
                        text_color = GREEN_TEXT
                    else:
                        row[result_idx] = 'Ожидание'
                        background_color = YELLOW_BACKGROUND
                        text_color = YELLOW_TEXT
                elif signal_type == '🟢 LONG':
                    if entry_price <= stop_loss:
                        row[result_idx] = 'Выбито по стоп лоссу'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = RED_BACKGROUND
                        text_color = RED_TEXT
                    elif entry_price >= take_profit:
                        row[result_idx] = 'Сделка сработана успешно'
                        row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                        row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                        background_color = GREEN_BACKGROUND
                        text_color = GREEN_TEXT
                    else:
                        row[result_idx] = 'Ожидание'
                        background_color = YELLOW_BACKGROUND
                        text_color = YELLOW_TEXT

            set_cell_colors(background_color, text_color, data, row)

        analytics.ws.update_values(crange=(2, 1), values=data)
    except Exception as e:
        print(e)

def set_cell_colors(background_color, text_color, data, row):
    if background_color and text_color:
        for col in COLS_TO_UPDATE:
            cell = analytics.ws.cell(f'{col}{data.index(row) + 2}')
            cell.color = background_color
            cell.set_text_format('foregroundColor', text_color)
            cell.update()

def schedule_tasks():
    aioschedule.every(60).minutes.do(update_analytics)

async def main():
    schedule_tasks()
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())
