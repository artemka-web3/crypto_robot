from binance import Client
from datetime  import datetime
import warnings
import threading
import time
from last_signal_dir_json import *
from combo import *
from config import *
import requests


# warnings.filterwarnings("ignore", category=FutureWarning)

# symbols = [
# "BTC/USDT",
# "ETH/USDT",
# "LTC/USDT",
# "TRX/USDT",
# "BNB/USDT",
# "LINK/USDT",
# "ADA/USDT",
# "DOT/USDT",
# "XRP/USDT",
# "CRV/USDT" 
# ]

threads = []


def run_crypto_tracker(symbols):
    global threads
    for sym in symbols:
        thread = threading.Thread(target=combo_strategy_full, args=(sym,))
        threads.append(thread)
        thread.start()
        time.sleep(1)

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
fullfill(symbols)
run_crypto_tracker(symbols)
for thread in threads:
    thread.join()