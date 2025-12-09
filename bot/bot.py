import os
import math
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from sqlalchemy.exc import IntegrityError
from aiogram.client.session.aiohttp import AiohttpSession
from api_v1.repositories import users_repository
from api_v1.schemas.users import UserCreate
from core.db_helper import get_session
from core import settings
from core.models import User
from aiogram.types import FSInputFile, LabeledPrice, PreCheckoutQuery
import requests

API_TOKEN = settings.BOT.bot_token
ADMIN_TG_ID = settings.BOT.admin_tg_id
CRYPTO_BOT_TOKEN = "341247:AAbEHSq8RtooEzgsTmO9F3y2KLb8ikmoSqv"

#настроить конфиги для токена и курсов
#разнести по файлам а то душно уже

cr_responses = {}
cr_amounts = {}

bt = Bot(token=API_TOKEN)
dp = Dispatcher()

router = Router()

async def stars_buying(tg_id: int,amount:int):
    await bt.send_invoice(
        chat_id=tg_id,
        title="Пополнения баланса",
        description=f"Пополнение баланса на {amount} рублей.",
        payload=f"order_{tg_id}_{amount}",
        currency="XTR",
        prices=[LabeledPrice(label="Цена", amount=int(amount* 1.8))],

        # reply_markup=payment_keyboard()
    )


def get_pay_link(amount):
    headers = {"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}
    data = {"asset": "USDT", "amount": amount}
    response = requests.post('https://pay.crypt.bot/api/createInvoice', headers=headers, json=data)
    if response.ok:
        response_data = response.json()
        return response_data['result']['pay_url'], response_data['result']['invoice_id']
    return None, None

def check_invoice_status(invoice_id):
    """Проверяет статус инвойса в Crypto Bot"""
    headers = {"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}
    response = requests.get(f'https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}', headers=headers)
    if response.ok:
        response_data = response.json()
        if response_data['result']['items']:
            invoice = response_data['result']['items'][0]
            return invoice['status'], float(invoice.get('amount', 0))
    return None, 0

async def crypto_replenishment(tg_id:int, amount:int):
    # Тестовая сумма в USDT (можно изменить или принимать от пользователя)
    amount = amount
    chat_id = tg_id

    us_amount = round(amount / 95, 2)
    # Сохраняем сумму для пользователя
    cr_amounts[chat_id] = us_amount

    # Получаем ссылку на оплату
    pay_link, invoice_id = get_pay_link(us_amount)

    if pay_link and invoice_id:
        # Сохраняем invoice_id для отслеживания платежа
        cr_responses[chat_id] = invoice_id

        # Отправляем пользователю ссылку на оплату
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 Оплатить", url=pay_link)],
            [types.InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_payment_{invoice_id}")]
        ])

        await bt.send_message(
            chat_id=chat_id, text=
            f"💰 Пополнение баланса на {us_amount} USDT\n\n"
            f"Нажмите кнопку ниже для оплаты через Crypto Bot.\n"
            f"После оплаты нажмите 'Проверить оплату'.",
            reply_markup=keyboard
        )
    else:
        await bt.send_message(chat_id=chat_id, text = "❌ Ошибка при создании счета. Попробуйте позже.")


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    payment_info = message.successful_payment
    # Конвертируем звезды обратно в рубли (payment_info.total_amount содержит количество звезд)
    # Используем math.ceil для округления к верхней границе
    rubles_amount = math.ceil(payment_info.total_amount / 1.8)
    async for session in get_session():
        await users_repository.add_balance(message.from_user.id, rubles_amount, session = session)
    await message.answer(
        f"🥳Спасибо за пополнения баланса на {rubles_amount}₽\n"
    )
session = AiohttpSession(timeout=60)
current_dir = os.path.dirname(__file__)

async def give_a_product(tg_id:int, product_title:str, product_data:str):
    bot = Bot(token=API_TOKEN)
    text =f"Товар: {product_title}. Выдача автомотическая"

    product_data = product_data.replace("\\", "/")
    file_path = os.path.join(current_dir, "..", product_data)
    file_path = os.path.normpath(file_path)

    document = FSInputFile(file_path)
    await bot.send_document(chat_id=tg_id, document=document, caption=text)
    await bot.session.close()




async def include_order(tg_id:int, username:str, order_id:int, items:dict, sum:int):
    bot = Bot(token=API_TOKEN)
    text = f" <b>Заказ №{order_id}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, (key, value) in enumerate(items.items()):
        text += f"     {i + 1}) {value} {key}\n\n"

    text += (f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
             f"💰 <b>Сумма заказа:</b> {sum}₽\n\n"
             f"📞 <b>Для получения заказа</b>\n"
            f"можешь "
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


@dp.message(Command(commands=["testbalancefunc"]))
async def cmd_replenishment(message: types.Message):
    await stars_buying(tg_id = message.from_user.id,amount = 4)

@dp.message(Command(commands=["testbalancefunccr"]))
async def cmd_replenishmentcr(message: types.Message):
    await crypto_replenishment(tg_id = message.from_user.id,amount = 4)

@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment_callback(callback: types.CallbackQuery):
    """Обработчик проверки статуса платежа"""
    invoice_id = callback.data.replace("check_payment_", "")

    # Проверяем статус платежа
    status, amount = check_invoice_status(invoice_id)

    if status == "paid":
        # Конвертируем USDT в рубли (курс можно настроить)
        usdt_to_rub = 95  # Примерный курс USDT к рублю
        rubles_amount = int(amount * usdt_to_rub)

        # Начисляем баланс пользователю
        async for session in get_session():
            await users_repository.add_balance(callback.from_user.id, rubles_amount, session=session)
            break

        await callback.answer("✅ Оплата подтверждена!")
        await callback.message.edit_text(
            f"✅ Оплата подтверждена!\n"
            f"На ваш баланс зачислено {rubles_amount}₽"
        )

        # Удаляем из кэша
        if callback.message.chat.id in cr_responses:
            del cr_responses[callback.message.chat.id]
        if callback.message.chat.id in cr_amounts:
            del cr_amounts[callback.message.chat.id]

    elif status == "active":
        await callback.answer("⏳ Платеж еще не поступил. Попробуйте позже.", show_alert=True)
    elif status == "expired":
        await callback.answer("❌ Счет истек. Создайте новый.", show_alert=True)
    else:
        await callback.answer("❌ Не удалось проверить статус платежа.", show_alert=True)




@dp.message(Command(commands=["profile"]))
async def cmd_profile(message: types.Message):
    async for session in get_session():
        profile = await users_repository.get_user(tg_id = message.from_user.id,session = session)
        await message.answer(f"Ваши данные {profile.username},{profile.balance}")
        break

# Подключаем роутер к диспетчеру
dp.include_router(router)

async def run_polling():
    try:
        await dp.start_polling(bt, skip_updates=True)
    finally:
        await bt.session.close()