import pygsheets

async def add_item(price, take_profit, stop_loss, time, take_perc, stop_perc):
    gc = pygsheets.authorize(service_account_file='sheets_key.json')
    ws = gc.open('Крипта стата').worksheet()
    prices = ws.get_col(1)
    for n,i in enumerate(prices):
        if i == '':
            prices = prices[:n]
            break
    ws.update_row(len(prices), list(map(str, [price, take_profit, stop_loss, time, take_perc, stop_perc])))