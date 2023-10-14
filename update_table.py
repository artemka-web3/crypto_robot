import analytics
import aioschedule
from signals_json import read_json
from combo import get_historical_data
import asyncio

async def update_analytics():
    signals = read_json()
    if signals:
        for item in signals:
            historical_data = get_historical_data(item['ticker'], '4h', 200)
            entry_price = historical_data['close'].iloc[-1]

            if item['signal_type'] == '🔴 SHORT':
                if entry_price > item['stop_loss']:
                    await analytics.update_item(item['ticker'], item['time'], 'stop loss')
                if entry_price < item['take_profit']:
                    await analytics.update_item(item['ticker'], item['time'], 'take profit')
                    return
            if item['signal_type'] == '🟢 LONG':
                if entry_price < item['stop_loss']:
                    await analytics.update_item(item['ticker'], item['time'], 'stop loss')
                    return
                if entry_price > item['take_profit']:
                    await analytics.update_item(item['ticker'], item['time'], 'take profit')
                    return


def schedule_tasks():
    aioschedule.every(5).seconds.do(update_analytics)


async def main():
    schedule_tasks()    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
asyncio.run(main())