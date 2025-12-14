import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from parser_text import parse
from db import safe_execute
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TG_BOT_TOKEN')
if not API_TOKEN:
    raise RuntimeError('TG_BOT_TOKEN not set in env')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await message.answer("Привет! Задай вопрос, например \"Сколько всего видео есть в системе?\"")

async def handle_message(message: types.Message):
    text = message.text or ''
    nlu = parse(text)
    print(nlu)
    if not nlu.get('ok'):
        await message.answer(
            'Непонятен запрос. Пожалуйста, уточните: укажите даты или период.'
        )
        return

    try:
        value = safe_execute(nlu['template_id'], nlu['params'])
    except Exception as e:
        logging.exception(e)
        await message.answer('Ошибка при выполнении запроса на сервере.')
        return

    await message.answer(str(value))


dp.message.register(handle_message)

async def main():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
