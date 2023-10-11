from signals_json import *
from prophet import Prophet
from fix_position import *
from statsmodels.tsa.arima.model import ARIMA

import talib
import ccxt
import time
import pandas as pd
import last_signal_dir_json

bollinger_period = 14
stoch_k_period = 14
stoch_d_period = 3
adx_period = 14
adx_threshold = 25

atr_period = 200  # Период для расчета ATR (можете настроить по своему усмотрению)
atr_multiplier = 2.0 

bitget = ccxt.binance()



def predict_price(historical_data, symbol):
    df_prophet = historical_data[['close']].reset_index()
    df_prophet.rename(columns={'timestamp': 'ds', 'close': 'y'}, inplace=True)
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=240, freq='min')
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(1)
    return forecast

def forecast_stop_loss(data, direction, num_values=3):
    close_prices = data['close'].values
    if direction == "LONG":
        # Прогноз для LONG
        model = ARIMA(close_prices, order=(5,1,0))  # Параметры модели могут варьироваться
    else:
        # Прогноз для SHORT
        model = ARIMA(close_prices, order=(5,1,0))  # Параметры модели могут варьироваться

    model_fit = model.fit()
    forecasted_values = model_fit.forecast(steps=num_values)
    return forecasted_values

def calculate_stop_loss(data, atr_period, atr_multiplier):
    atr = talib.ATR(data['high'], data['low'], data['close'], timeperiod=atr_period)
    last_atr = atr.iloc[-1]
    stop_loss_price = data['close'].iloc[-1] - (atr_multiplier * last_atr)
    return stop_loss_price

def get_historical_data(symbol, timeframe, limit):
    ohlcv = bitget.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def calculate_indicators(data):
    bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(data['close'], timeperiod=bollinger_period)
    stoch_k, stoch_d = talib.STOCH(data['high'], data['low'], data['close'], fastk_period=stoch_k_period, slowk_period=stoch_d_period)
    adx = talib.ADX(data['high'], data['low'], data['close'], timeperiod=adx_period)
    return bollinger_upper, bollinger_middle, bollinger_lower, stoch_k, stoch_d, adx

# Основная стратегия
def combo_strategy_full(symbol):
    while True:
        historical_data = get_historical_data(symbol, '4h', 200)
        bollinger_upper, bollinger_middle, bollinger_lower, stoch_k, stoch_d, adx = calculate_indicators(historical_data)

        entry_price = historical_data['close'].iloc[-1]
        data = read_json()
        last_signals = last_signal_dir_json.read_last_signal_dir()
        if stoch_k.iloc[-1] > stoch_d.iloc[-1] and bollinger_lower.iloc[-1] > historical_data['close'].iloc[-1] and adx.iloc[-1] > adx_threshold:
            if last_signals[symbol] != "buy" and entry_price > 1:
                predicted_values = predict_price(historical_data, symbol)
                stop_loss_price = choose_stop_loss_pivot(historical_data, 'LONG')
                take_profit_price = predicted_values['yhat_upper'].iloc[-1]
                long_fixations = fix_position_long(entry_price, take_profit_price)
                take_procent_difference = ((take_profit_price - entry_price) / entry_price) * 100
                stop_procent_difference = ((entry_price - stop_loss_price) / stop_loss_price) * 100
                print(last_signals[symbol])
                print('', entry_price > stop_loss_price and entry_price < take_profit_price)

                if entry_price > stop_loss_price and entry_price < take_profit_price:
                    #обновление направления
                    last_signals[symbol] = 'buy'
                    last_signal_dir_json.write_last_signal_dir(last_signals)
                    #обновление направления
                    new_signal = {
                        "stop_loss": stop_loss_price,
                        "take_profit": take_profit_price,
                        "price": entry_price,
                        "signal_type": "🟢 LONG",
                        "ticker": symbol, 
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'fixations': long_fixations,
                        'take_perc': take_procent_difference,
                        'stop_perc': stop_procent_difference

                    }
                    data.append(new_signal)
                    write_json(data)
        elif stoch_k.iloc[-1] < stoch_d.iloc[-1] or bollinger_upper.iloc[-1] < historical_data['close'].iloc[-1]:
            if last_signals[symbol] != "sell" and entry_price > 1:

                predicted_values = predict_price(historical_data, symbol)
                stop_loss_price = choose_stop_loss_pivot(historical_data, 'SHORT')
                #stop_loss_price = calculate_stop_loss(historical_data, atr_period, atr_multiplier)
                # if stop_loss_price < entry_price:
                take_profit_price = predicted_values['yhat_lower'].iloc[-1]
                short_fixations = fix_position_short(entry_price, take_profit_price)
                take_procent_difference = ((entry_price - take_profit_price) / take_profit_price) * 100
                stop_procent_difference = ((stop_loss_price - entry_price) / entry_price) * 100

                if entry_price < stop_loss_price and entry_price > take_profit_price:
                    #обновление направления
                    last_signals[symbol] = 'sell'
                    last_signal_dir_json.write_last_signal_dir(last_signals)
                    #обновление направления
                    new_signal = {
                        "stop_loss": stop_loss_price,
                        "take_profit": take_profit_price,
                        "price": entry_price,
                        "signal_type": "🔴 SHORT",
                        "ticker": symbol, 
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'fixations': short_fixations,
                        'take_perc': take_procent_difference,
                        'stop_perc': stop_procent_difference
                    }
                    data.append(new_signal)
                    write_json(data)
               

        time.sleep(15)
    