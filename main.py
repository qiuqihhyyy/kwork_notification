import asyncio
import time
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm import storage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import psutil
import random


from config import settings
from database import OrderDAO
from parser import get_projects, work

logger = logging.getLogger(__name__)


# функция цикличного повторения
def repeat(coro, loop):
    # я не знаю для чего это

    asyncio.ensure_future(coro(), loop=loop)
    # выполнение coro раз в минуту бесконечно долго
    loop.call_later(random.randint(30, 90), repeat, coro, loop)

# главная функция
async def main():

    # установление логов
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # FSM состояния
    storage = MemoryStorage()
    bot = Bot(token=settings.get_token())
    dp = Dispatcher(storage=storage)

    # создание задачи
    loop = asyncio.get_event_loop()
    # постоянное повторение start_end_raffle раз в минуту
    loop.call_later(60, repeat, work, loop)

    # удаления веб хуков
    await bot.delete_webhook(drop_pending_updates=True)
    # начало работы бота
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())