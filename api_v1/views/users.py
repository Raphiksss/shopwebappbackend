import redis.asyncio as aioredis
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, Form, HTTPException

from core.db_helper import get_session
from ..schemas.users import UserRead, UserCreate, UserPartialUpdate
from ..services import users_services
from ..repositories import users_repository
from ..repositories.users import UserBy
from ..schemas.general import ErrorResponse
from ..services.Yoomoney import create_invoice, verify_webhook_signature
from api_v1.views.dependencies import get_client_auth_service, get_users_tg_id
from api_v1.services.client_auth import ClientAuthService, AccessPayload
from api_v1.services import admin_auth
from core import settings, logger

router = APIRouter(tags=["Users"])

class LoginRequest(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/login/",
    summary="Login User",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def login_user(login_data: LoginRequest, auth_service:ClientAuthService = Depends(get_client_auth_service)):
    access_token = await auth_service.login(login_data.init_data)
    return TokenResponse(access_token=access_token)

@router.get(
    "/me/",
    summary="Get User Data",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
)
async def get_current_user_data(tg_id:int = Depends(get_users_tg_id), session: AsyncSession = Depends(get_session)):
    return await users_repository.get_user(session, UserBy.TG_ID, tg_id)

@router.get(
    "/",
    summary="Get Users",
    status_code=status.HTTP_200_OK,
    response_model=list[UserRead],
)
async def get_users(session: AsyncSession = Depends(get_session), _=Depends(admin_auth.check_if_auth)):
    return await users_repository.get_users(session)


@router.post(
    "/",
    summary="Create User",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Пользователь с таким tg_id уже существует",
        }
    },
)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session), _=Depends(admin_auth.check_if_auth)):
    return await users_services.create_user(user, session)


@router.get(
    "/{tg_id}/",
    summary="Get User by tg_id",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    responses={
        404: {"model": ErrorResponse, "description": "Пользователя не существует"}
    },
)
async def get_user(tg_id: int,
                   session: AsyncSession = Depends(get_session),
                    _=Depends(admin_auth.check_if_auth),
):
    return await users_services.get_user(session, UserBy.TG_ID, tg_id)


@router.patch(
    "/{user_id}/",
    summary="Partial user update",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    responses={
        401: {"model": ErrorResponse, "description": "Не авторизован"},
        404: {"model": ErrorResponse, "description": "Пользователя не существует"},
    },
)
async def user_partial_update(
    user_id: int,
    new_user: UserPartialUpdate,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_auth.check_if_auth),
):
    return await users_services.update_user_partial(user_id, new_user, session)


@router.post(
    "/replenisment/stars/",
    summary="Создания счета на оплату звезды",
    status_code=status.HTTP_200_OK,
)
async def replenishment_balance(amount: int, tg_id: int = Depends(get_users_tg_id)):
    return await users_services.replenishment_balance_stars(tg_id, amount)


@router.post(
    "/replenisment/crypto/",
    summary="Создания счета на оплату криптобот",
    status_code=status.HTTP_200_OK,
)
async def replenishment_balance_cr(amount: int, tg_id: int = Depends(get_users_tg_id)):
    return await users_services.replenishment_balance_crypto_bot(tg_id, amount)


@router.post(
    "/replenisment/yoomoney/",
    summary="Создания счета на оплату Юмани",
    status_code=status.HTTP_200_OK,
)
async def replenishment_balance_yoomoney(amount: int, tg_id: int = Depends(get_users_tg_id)):
    return await create_invoice(tg_id, amount)


@router.post(
    "/webhook/yoomoney/", summary="Webhook от YooMoney", status_code=status.HTTP_200_OK
)
async def yoomoney_webhook(
    notification_type: str = Form(...),
    operation_id: str = Form(...),
    amount: str = Form(...),
    currency: str = Form(...),
    datetime: str = Form(...),
    sender: str = Form(""),
    codepro: str = Form(...),
    label: str = Form(...),
    sha1_hash: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    # 1. Формируем payload (все значения как строки - как их отправляет YooMoney)
    payload = {
        "notification_type": notification_type,
        "operation_id": operation_id,
        "amount": amount,
        "currency": currency,
        "datetime": datetime,
        "sender": sender,
        "codepro": codepro,
        "label": label,
        "sha1_hash": sha1_hash,
    }

    logger.debug(f"[YooMoney Webhook] Received: {payload}")
    logger.debug(
        f"[YooMoney Webhook] Secret length: {len(settings.YOOMONEY_NOTIFICATION_SECRET)}"
    )

    # 2. Проверка подписи
    if not await verify_webhook_signature(payload):
        logger.warn(f"[YooMoney Webhook] Signature verification FAILED")
        raise HTTPException(status_code=403, detail="Invalid signature")

    logger.debug(f"[YooMoney Webhook] Signature verification OK")

    # 3. Валидация amount
    amount_float = float(amount)
    if amount_float <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # 4. Защита от дублирования через Redis
    redis_client = aioredis.Redis(
        host=settings.DB.REDIS_HOST, port=settings.DB.REDIS_PORT, decode_responses=True
    )

    try:
        key = f"yoomoney_processed:{label}"
        # SET NX EX - atomic операция
        is_new = await redis_client.set(key, "1", nx=True, ex=604800)  # 7 дней

        if not is_new:
            await redis_client.close()
            return {"status": "ok", "message": "Already processed"}

        # 5. Извлечение tg_id из label (формат: order_{tg_id}_{timestamp})
        try:
            parts = label.split("_")
            tg_id = int(parts[1])
        except (IndexError, ValueError):
            await redis_client.delete(key)
            await redis_client.close()
            raise HTTPException(status_code=400, detail="Invalid label format")

        # 6. Обновление баланса
        try:
            await users_repository.add_balance(tg_id, int(float(amount)), session)
        except Exception as e:
            await redis_client.delete(key)
            await redis_client.close()
            raise HTTPException(
                status_code=500, detail=f"Failed to update balance: {str(e)}"
            )

        await redis_client.close()
        return {"status": "ok"}

    except Exception as e:
        await redis_client.close()
        raise
