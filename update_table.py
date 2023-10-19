import analytics
import aioschedule
import asyncio
import gspread_formatting as gsf
from signals_json import read_json
from combo import get_historical_data
from datetime import datetime, timedelta
from config import *

col_arr =  ["I", 'J', 'K']

async def update_analytics():
    # Открываем Google Sheets и получаем данные
    print('Проход по сиганалам')
    data = ws.get_all_values(returnas='matrix')

    # Пропускаем заголовок
    header = data[0]
    data = data[63:]

    # Индексы столбцов
    ticker_idx = header.index('Тикер')
    signal_type_idx = header.index('Тип сигнала')
    take_profit_idx = header.index('Тейк профит')
    stop_loss_idx = header.index('Стоп лосс')
    time_idx = header.index('Время сигнала')
    result_idx = header.index('Результат')
    time_result_idx = header.index('Время достижения цели (дата+ часы:минуты) ')
    deadline_idx = header.index('Срок достижения результата')
    try:
        for row in data:
            
            ticker = row[ticker_idx]
            signal_type = row[signal_type_idx]
            take_profit = float(row[take_profit_idx])
            stop_loss = float(row[stop_loss_idx])
            entry_time = datetime.strptime(row[time_idx], "%Y-%m-%d %H:%M")
            current_time = datetime.now()
            #deadline = entry_time + timedelta(hours=int(row[deadline_idx]))

            historical_data = get_historical_data(ticker, '4h', 200, bitget)
            entry_price = historical_data['close'].iloc[-1]

            if signal_type == '🔴 SHORT':
                if entry_price >= stop_loss:
                    row[result_idx] = 'Выбито по стоп лоссу'
                    row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                    row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                    background_color = (1, 0.8, 0.8)  # Светло-красный фон
                    text_color = (0.4, 0, 0, 1.0)  # Темно-красный текст
                    set_cell_colors(background_color, text_color, data, row)

                elif entry_price <= take_profit:
                    row[result_idx] = 'Сделка сработана успешно'
                    row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                    row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                    background_color = (0.8, 1, 0.8)  # Светло-зеленый фон
                    text_color = (0, 0.4, 0, 1.0)  # Темно-зеленый текст
                    set_cell_colors(background_color, text_color, data, row)

                else:
                    row[result_idx] = 'Ожидание'
                    background_color = (1, 1, 0.8)  # Светло-желтый фон
                    text_color = (0.4, 0.4, 0, 1.0) # Темно-желтый текст
                    set_cell_colors(background_color, text_color, data, row)


            if signal_type == '🟢 LONG':
                if entry_price <= stop_loss:
                    row[result_idx] = 'Выбито по стоп лоссу'
                    row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                    row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                    background_color = (1, 0.8, 0.8)  # Светло-красный фон
                    text_color = (0.4, 0, 0, 1.0)  # Темно-красный текст
                    set_cell_colors(background_color, text_color)
                elif entry_price >= take_profit:
                    row[result_idx] = 'Сделка сработана успешно'
                    row[time_result_idx] = current_time.strftime("%Y-%m-%d %H:%M")
                    row[deadline_idx] = int((current_time - entry_time).total_seconds() / 60)
                    background_color = (0.8, 1, 0.8)  # Светло-зеленый фон
                    text_color = (0, 0.4, 0, 1.0)  # Темно-зеленый текст
                    set_cell_colors(background_color, text_color, data, row)
                else:
                    row[result_idx] = 'Ожидание'
                    background_color = (1, 1, 0.8, 1.0)  # Light yellow background with full alpha
                    text_color = (0.4, 0.4, 0, 1.0)
                    set_cell_colors(background_color, text_color, data, row)
            ws.update_values(crange=(2, 1), values=data)
    except Exception as e:
        print(e)


def set_cell_colors(background_color, text_color, data, row):
    for i in col_arr:
        cell = ws.cell(f'{i}{data.index(row) + 2}')  # Пропускаем заголовок
        cell.color = background_color  # Установите цвет фона
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