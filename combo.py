import asyncio
import pandas as pd
import talib
import ccxt
from fix_position import choose_stop_loss_pivot
from json_utils import *
from prophet import Prophet

async def calculate_stop_loss(data, atr_period, atr_multiplier):
    atr = talib.ATR(data['high'], data['low'], data['close'], timeperiod=atr_period)
    last_atr = atr.iloc[-1]
    stop_loss_price = data['close'].iloc[-1] - (atr_multiplier * last_atr)
    return stop_loss_price

async def calculate_indicators(data):
    bollinger_period = 14
    stoch_k_period = 14
    stoch_d_period = 3
    adx_period = 14

    bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(data['close'], timeperiod=bollinger_period)
    stoch_k, stoch_d = talib.STOCH(data['high'], data['low'], data['close'], fastk_period=stoch_k_period, slowk_period=stoch_d_period)
    adx = talib.ADX(data['high'], data['low'], data['close'], timeperiod=adx_period)
    return bollinger_upper, bollinger_middle, bollinger_lower, stoch_k, stoch_d, adx

async def get_historical_data(symbol, timeframe, limit):
    bitget = ccxt.binance()
    ohlcv = bitget.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

async def predict_price(historical_data):
    df_prophet = historical_data[['close']].reset_index()
    df_prophet.rename(columns={'timestamp': 'ds', 'close': 'y'}, inplace=True)
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=240, freq='min')
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(100)
    return forecast

async def combo_strategy_long(symbol, historical_data, entry_price, last_signals):
    data = await read_signals()
    stop_loss_price = choose_stop_loss_pivot(historical_data, 'LONG')
    take_profit_points = await predict_price(historical_data)
    take_profit_points = [take_profit_points['yhat_upper'].iloc[-1], take_profit_points['yhat_upper'].iloc[-30], take_profit_points['yhat_upper'].iloc[-60], take_profit_points['yhat_upper'].iloc[-90]]
    take_profit_points.sort()
    take_profit_price = take_profit_points[3]
    long_fixations = [take_profit_points[0], take_profit_points[1], take_profit_points[2]]
    take_procent_difference = ((take_profit_price - entry_price) / entry_price) * 100
    stop_procent_difference = ((entry_price - stop_loss_price) / stop_loss_price) * 100

    if entry_price > stop_loss_price and entry_price < take_profit_price and take_procent_difference > stop_procent_difference:
        last_signals[symbol] = 'buy'
        await write_last_signal_dir(last_signals)
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
        await write_signals(data)

async def combo_strategy_short(symbol, historical_data, entry_price, last_signals):
    data = await read_signals()
    stop_loss_price = await choose_stop_loss_pivot(historical_data, 'SHORT')
    take_profit_points = await predict_price(historical_data, symbol)
    take_profit_points = [take_profit_points['yhat_lower'].iloc[-1], take_profit_points['yhat_lower'].iloc[-30], take_profit_points['yhat_lower'].iloc[-60], take_profit_points['yhat_lower'].iloc[-89]]
    take_profit_points.sort()
    take_profit_price = take_profit_points[0]
    short_fixations = [take_profit_points[3], take_profit_points[2], take_profit_points[1]]
    take_procent_difference = ((entry_price - take_profit_price) / take_profit_price) * 100
    stop_procent_difference = ((stop_loss_price - entry_price) / entry_price) * 100

    if entry_price < stop_loss_price and entry_price > take_profit_price and take_procent_difference > stop_procent_difference:
        last_signals[symbol] = 'sell'
        await write_last_signal_dir(last_signals)
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
        await write_signals(data)

async def combo_strategy_full(symbol):
    adx_threshold = 25
    while True:
        historical_data = await get_historical_data(symbol, '4h', 200)
        bollinger_upper, bollinger_middle, bollinger_lower, stoch_k, stoch_d, adx =await  calculate_indicators(historical_data)
        entry_price = historical_data['close'].iloc[-1]
        last_signals = await read_last_signal_dir()
        if stoch_k.iloc[-1] > stoch_d.iloc[-1] and bollinger_lower.iloc[-1] > historical_data['close'].iloc[-1] and adx.iloc[-1] > adx_threshold:
            if last_signals[symbol] != "buy" and entry_price > 1:
                await combo_strategy_long(symbol, historical_data, entry_price, last_signals)
        elif stoch_k.iloc[-1] < stoch_d.iloc[-1] or bollinger_upper.iloc[-1] < historical_data['close'].iloc[-89]:
            if last_signals[symbol] != "sell" and entry_price > 1:
                await combo_strategy_short(symbol, historical_data, entry_price, last_signals)
        asyncio.sleep(15)
    