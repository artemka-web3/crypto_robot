import aioschedule
import asyncio
from analytics import update_sheet


def schedule_tasks():
    aioschedule.every(60).minutes.do(update_sheet)

async def main():
    await update_sheet()
    schedule_tasks()
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())
