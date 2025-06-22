import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from api_users.crud import create_user, get_user
from api_users.schemas import UserCreate
from core.db_helper import get_session
from core import settings


API_TOKEN = settings.bot_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher()



@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    new_user = UserCreate(tg_id = message.from_user.id,username = message.from_user.username, balance = 0)
    async for session in get_session():
        user = await create_user(session = session,user_in = new_user)
        break
    await message.answer("Привет")

@dp.message(Command(commands=["profile"]))
async def cmd_profile(message: types.Message):
    async for session in get_session():
        profile = await get_user(tg_id = message.from_user.id,session = session)
        await message.answer(f"Ваши данные {profile.username},{profile.balance}")
        break

async def run_polling():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()