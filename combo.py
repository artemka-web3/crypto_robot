from signals_json import *
from prophet import Prophet
from fix_position import *
from statsmodels.tsa.arima.model import ARIMA

import talib
import time
import pandas as pd
import last_signal_dir_json
import ccxt
from datetime import timedelta



def predict_price(historical_data, symbol):
    df_prophet = historical_data[['close']].reset_index()
    df_prophet.rename(columns={'timestamp': 'ds', 'close': 'y'}, inplace=True)
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=240, freq='min')
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(1)
    return forecast

def get_historical_data(symbol, timeframe, limit, bitget):
    ohlcv = bitget.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def calculate_indicators(data):
    # RSI (Relative Strength Index)
    rsi_period = 14
    rsi = talib.RSI(data['close'], timeperiod=rsi_period)

    # MACD (Moving Average Convergence Divergence)
    macd, signal, _ = talib.MACD(data['close'])

    # Simple Moving Averages (SMA)
    short_sma_period = 50
    long_sma_period = 200
    short_sma = talib.SMA(data['close'], timeperiod=short_sma_period)
    long_sma = talib.SMA(data['close'], timeperiod=long_sma_period)

    return rsi, macd, short_sma, long_sma

# Основная стратегия
def combo_strategy_full(symbol, bitget):
    rsi_threshold = 30
    while True:
        historical_data = get_historical_data(symbol, '4h', 200, bitget)
        rsi, macd, short_sma, long_sma = calculate_indicators(historical_data)
        entry_price = historical_data['close'].iloc[-1]
        data = read_json()
        last_signals = last_signal_dir_json.read_last_signal_dir()
        if rsi.iloc[-1] < rsi_threshold and macd.iloc[-1] > 0 and short_sma.iloc[-1] > long_sma.iloc[-1]:
            if last_signals[symbol]['last_signal'] != "buy" and entry_price > 1 and datetime.strptime(last_signals[symbol]['last_time'], "%Y-%m-%d %H:%M") < datetime.now() - timedelta(hours=1):
                stop_loss_price = choose_stop_loss_pivot(historical_data, 'LONG')
                take_profit_points =  predict_price(historical_data, symbol)
                take_profit_price = take_profit_points['yhat_upper'].iloc[-1]
                take_procent_difference = ((take_profit_price - entry_price) / entry_price) * 100
                stop_procent_difference = ((entry_price - stop_loss_price) / stop_loss_price) * 100
                #print(last_signals[symbol])
                #print('', entry_price > stop_loss_price and entry_price < take_profit_price)

                if entry_price > stop_loss_price and entry_price < take_profit_price and take_procent_difference > stop_procent_difference:
                    #обновление направления
                    last_signals[symbol]['last_signal'] = 'buy'
                    last_signals[symbol]['last_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                    last_signal_dir_json.write_last_signal_dir(last_signals)
                    #обновление направления
                    new_signal = {
                        "stop_loss": stop_loss_price,
                        "take_profit": take_profit_price,
                        "price": entry_price,
                        "signal_type": "🟢 LONG",
                        "ticker": symbol, 
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'take_perc': take_procent_difference,
                        'stop_perc': stop_procent_difference

                    }
                    data.append(new_signal)
                    write_json(data)
        elif rsi.iloc[-1] > 70 and macd.iloc[-1] < 0 and short_sma.iloc[-1] < long_sma.iloc[-1]:
            if last_signals[symbol] != "sell" and entry_price > 1 and datetime.strptime(last_signals[symbol]['last_time'], "%Y-%m-%d %H:%M") < datetime.now() - timedelta(hours=1):

                stop_loss_price = choose_stop_loss_pivot(historical_data, 'SHORT')

                take_profit_points =  predict_price(historical_data, symbol)
                take_profit_price = take_profit_points['yhat_lower'].iloc[-1]

                take_procent_difference = ((entry_price - take_profit_price) / take_profit_price) * 100
                stop_procent_difference = ((stop_loss_price - entry_price) / entry_price) * 100

                if entry_price < stop_loss_price and entry_price > take_profit_price and take_procent_difference > stop_procent_difference:
                    #обновление направления
                    last_signals[symbol]['signal_type'] = 'sell'
                    last_signals[symbol]['last_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')

                    last_signal_dir_json.write_last_signal_dir(last_signals)
                    #обновление направления
                    new_signal = {
                        "stop_loss": stop_loss_price,
                        "take_profit": take_profit_price,
                        "price": entry_price,
                        "signal_type": "🔴 SHORT",
                        "ticker": symbol, 
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'take_perc': take_procent_difference,
                        'stop_perc': stop_procent_difference
                    }
                    data.append(new_signal)
                    write_json(data)
               

        time.sleep(15)
    