
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.exc import IntegrityError
from aiogram.client.session.aiohttp import AiohttpSession
from api_v1.repositories import users_repository
from api_v1.schemas.users import UserCreate
from core.db_helper import get_session
from core import settings
from core.models import User

API_TOKEN = settings.BOT.bot_token
ADMIN_TG_ID = settings.BOT.admin_tg_id

bt = Bot(token=API_TOKEN)
dp = Dispatcher()
session = AiohttpSession(timeout=60)

async def include_order(tg_id:int, username:str, order_id:int, items:dict, sum:int):
    bot = Bot(token=API_TOKEN)
    text = f" <b>Заказ №{order_id}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, (key, value) in enumerate(items.items()):
        text += f"     {i + 1}) {value} {key}\n\n"

    text += (f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
             f"💰 <b>Сумма заказа:</b> {sum}₽\n\n"
             f"📞 <b>Для получения заказа</b>\n"
            f"Напишите менеджеру: @raphiks\n\n"
             f"✅ <i>Спасибо за ваш заказ!</i>")

    await bot.send_message(chat_id= tg_id, text=text, parse_mode='HTML')
    admin_text = f"Был оформлен заказ на @{username}\n\n"+text
    await bot.send_message(chat_id=ADMIN_TG_ID, text=admin_text, parse_mode='HTML' )
    await bot.session.close()

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
        await dp.start_polling(bt, skip_updates=True)
    finally:
        await bt.session.close()