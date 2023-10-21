import pygsheets
import pytz
import datetime

gc = pygsheets.authorize(service_account_file='sheets_key.json')
ws = gc.open('Крипта стата').worksheet()


async def add_item(ticker, price, take_profit, stop_loss, time, take_perc, stop_perc, signal_type):
    tickers = ws.get_col(1)
    for n,i in enumerate(tickers):
        if i == '':
            tickers = tickers[:n]
            break
    ws.update_row(len(tickers)+1, list(map(str, [ticker, signal_type, price, take_profit, stop_loss, time, take_perc, stop_perc])))

async def update_item(ticker, time, result):
    tickers = ws.get_col(1)
    for n,i in enumerate(tickers):
        if i == ticker:
            tickers = tickers[:n]
            row = ws.get_row(n)
            if row[4] == time:
                tickers = tickers[:n]
                break
    time_goal = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    duration = time_goal - datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
    ws.update_row(n+1, list(map(str, [ticker, row[1], row[2], row[3], time, row[5], row[6], result, time_goal, duration])))