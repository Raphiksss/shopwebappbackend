from fastapi import APIRouter, Depends

from api_v1.schemas.settings import (
    AssentColor,
    StarsExchangeRate,
    BotToken,
    CryptoBotToken,
    YooMoneyData,
    PaymentMethods,
)
from api_v1.services.auth import check_if_auth
from api_v1.services.settings import (
    change_accent_color,
    get_accent_color,
    change_stars_exchange_rate,
    get_stars_exchange_rate,
    change_bot_token,
    get_bot_token,
    change_crypto_bot_token,
    get_crypto_bot_token,
    change_yoomoney_data,
    get_yoomoney_data,
    change_payment_methods,
    get_payment_methods,
)
from api_v1.schemas.general import ErrorResponse

router = APIRouter(tags=["Settings"])


@router.post(
    "/accent_color/",
    summary="Set accent color",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_accent_color(color: AssentColor, _=Depends(check_if_auth)):
    return await change_accent_color(color.color)


@router.get("/accent_color/", summary="Get accent color")
async def accent_color():
    return await get_accent_color()


@router.post(
    "/stars_exchange_rate/",
    summary="Set stars exchange rate",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_stars_exchange_rate(
    exchange_rate: StarsExchangeRate, _=Depends(check_if_auth)
):
    return await change_stars_exchange_rate(exchange=exchange_rate.exchange_rate)


@router.get("/stars_exchange_rate/", summary="Get stars exchange rate")
async def stars_exchange_rate():
    return await get_stars_exchange_rate()


@router.post(
    "/bot_token/",
    summary="Set bot token",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_bot_token(bot_token: BotToken, _=Depends(check_if_auth)):
    return await change_bot_token(bot_token.bot_token)


@router.get(
    "/bot_token/",
    summary="Get bot token",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def bot_token(_=Depends(check_if_auth)):
    return await get_bot_token()


@router.post(
    "/crypto_token/",
    summary="Set crypto_bot token",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_crypto_bot_token(
    crypto_bot_token: CryptoBotToken, _=Depends(check_if_auth)
):
    return await change_crypto_bot_token(crypto_bot_token.crypto_bot_token)


@router.get(
    "/crypto_token/",
    summary="Get crypto_bot token",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def crypto_bot_token(_=Depends(check_if_auth)):
    return await get_crypto_bot_token()


@router.post(
    "/yoo_money/",
    summary="Set yoomoney data",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_yoomoney_data(yoomoney: YooMoneyData, _=Depends(check_if_auth)):
    return await change_yoomoney_data(yoomoney)


@router.get(
    "/yoo_money/",
    summary="Get yoomoney data",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def yoomoney_data(_=Depends(check_if_auth)):
    return await get_yoomoney_data()


@router.post(
    "/payment_methods/",
    summary="Set payment_methods",
    responses={401: {"model": ErrorResponse, "description": "Не авторизован"}},
)
async def set_payments_methods(payments: PaymentMethods, _=Depends(check_if_auth)):
    return await change_payment_methods(payments)


@router.get(
    "/payment_methods/", summary="Get payment_methods", response_model=PaymentMethods
)
async def payments_methods():
    return await get_payment_methods()
