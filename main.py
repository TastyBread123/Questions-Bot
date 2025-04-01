import logging
from asyncio import run
from aiogram import Dispatcher, Bot, types

from config import TOKEN
from database.base import init_database, close_database
from handlers.commands import routers

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

async def main():
    """Главный поток"""

    commands = [
        types.BotCommand(command='start', description='главное меню')
    ]

    dp.include_routers(*routers)
    await init_database()
    await bot.set_my_commands(commands)
    await dp.start_polling(bot, allowed_updates=["message", 'callback_query'])
    await close_database()


@dp.shutdown()
async def on_shutdown():
    # Действие при выключении бота
    await close_database()


if __name__ == '__main__':
    run(main())
