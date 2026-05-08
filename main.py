import logging, asyncio
from maxapi import Dispatcher, Bot
from maxapi.enums.parse_mode import ParseMode

from config import TOKEN
from database.base import init_database, close_database
from handlers import routers

logging.basicConfig(format="%(asctime)s %(levelname)s (%(filename)s).%(funcName)s(%(lineno)d): %(message)s", level=logging.INFO)
bot = Bot(TOKEN, parse_mode=ParseMode.HTML, disable_link_preview=True)
dp = Dispatcher()

async def main():
    """Главный поток"""

    dp.include_routers(*routers)
    await init_database()
    await bot.delete_webhook()
    await dp.start_polling(bot, skip_updates=True)
    await close_database()



if __name__ == '__main__':
    asyncio.run(main())
