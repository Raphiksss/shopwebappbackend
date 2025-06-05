import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = "7971991234:AAEGi3z3rpEcmzMI8PN3HQJtC0j7ipY-rHk"


bot = Bot(token=API_TOKEN)

dp = Dispatcher()


@dp.message(Command(commands=["start"]))
async def cmd_start_handler(message: types.Message):
    await message.answer("Привет! Я бот на aiogram 3.x, запущенный вместе с FastAPI.")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")


async def run_polling():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()