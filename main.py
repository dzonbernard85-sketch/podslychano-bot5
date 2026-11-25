# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import STUDENT_BOT_TOKEN, MODERATOR_BOT_TOKEN
from student_bot import register_student_handlers
from moderator_bot import register_moderator_handlers

logging.basicConfig(level=logging.INFO)

async def main():
    student_bot = Bot(token=STUDENT_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    moderator_bot = Bot(token=MODERATOR_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    student_dp = Dispatcher()
    moderator_dp = Dispatcher()

    register_student_handlers(student_dp, student_bot, moderator_bot)
    register_moderator_handlers(moderator_dp, moderator_bot)

    print("Боты успешно запущены!")
    await asyncio.gather(
        student_dp.start_polling(student_bot),
        moderator_dp.start_polling(moderator_bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass