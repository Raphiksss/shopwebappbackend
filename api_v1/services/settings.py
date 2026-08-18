from redis import asyncio as aioredis
from fastapi import HTTPException
from core import settings
from ..schemas.settings import YooMoneyData, PaymentMethods

REDIS_HOST = settings.DB.REDIS_HOST
REDIS_PORT = settings.DB.REDIS_PORT


async def change_accent_color(accent_color: str):
    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.set("accent_color", accent_color)
    return {"accent_color": accent_color}


async def get_accent_color():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        accent_color = await r.get("accent_color")
    return {"accent_color": accent_color}


async def change_stars_exchange_rate(exchange: float):
    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.set("stars_exchange_rate", exchange)
    return {"stars_exchange_rate": exchange}


async def get_stars_exchange_rate():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        exchange = await r.get("stars_exchange_rate")
    return {"stars_exchange_rate": float(exchange)}


async def change_bot_token(bot_token: str):
    from bot.bot import restart_polling

    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.set("bot_token", bot_token)
    await restart_polling()
    return {"bot_token": bot_token}


async def get_bot_token():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        bot_token = await r.get("bot_token")
    return {"bot_token": bot_token}


async def change_crypto_bot_token(crypto_bot_token: str):
    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.set("crypto_bot_token", crypto_bot_token)
    return {"crypto_bot_token": crypto_bot_token}


async def get_crypto_bot_token():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        crypto_bot_token = await r.get("crypto_bot_token")
    return {"crypto_bot_token": crypto_bot_token}


async def change_yoomoney_data(yoomoney: YooMoneyData):
    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.json().set(
            "yoomoney_data",
            "$",
            {
                "token": yoomoney.token,
                "wallet": yoomoney.wallet,
                "notification_secret": yoomoney.notification_secret,
            },
        )
    return yoomoney


async def get_yoomoney_data():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        data = await r.json().get("yoomoney_data")
    return data


async def change_payment_methods(payments: PaymentMethods):
    async with aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        await r.json().set(
            "payment_methods",
            "$",
            {
                "stars": payments.stars,
                "crypto_bot": payments.crypto_bot,
                "yoomoney": payments.yoomoney,
            },
        )
    return payments


async def get_payment_methods():
    async with aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    ) as r:
        payments = await r.json().get("payment_methods")
    return payments
