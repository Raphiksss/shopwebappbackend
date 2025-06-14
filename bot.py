import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from api_users.crud import create_user
from api_users.schemas import UserCreate
from core.db_helper import get_session


API_TOKEN = "7971991234:AAEGi3z3rpEcmzMI8PN3HQJtC0j7ipY-rHk"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()



@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    new_user = UserCreate(tg_id = message.from_user.id,username = message.from_user.username, balance = 0)
    async for session in get_session():
        user = await create_user(session = session,user_in = new_user)
        break
    await message.answer("Привет")


async def run_polling():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()