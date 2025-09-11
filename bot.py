
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.exc import IntegrityError

from api_v1.repositories import users_repository
from api_v1.schemas.users import UserCreate
from core.db_helper import get_session
from core import settings
from core.models import User

API_TOKEN = settings.bot_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher()



@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    user = User(tg_id = message.from_user.id,username = message.from_user.username, balance = 0)
    async for session in get_session():
        try:
            await users_repository.create_user(session = session,user = user)
            await message.answer("Привет")
        except IntegrityError:
            await message.answer("Привет снова")
            break
        break


@dp.message(Command(commands=["profile"]))
async def cmd_profile(message: types.Message):
    async for session in get_session():
        profile = await users_repository.get_user(tg_id = message.from_user.id,session = session)
        await message.answer(f"Ваши данные {profile.username},{profile.balance}")
        break

async def run_polling():
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()