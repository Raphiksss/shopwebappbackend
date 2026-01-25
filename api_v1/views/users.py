from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from ..schemas.users import UserRead, UserCreate
from ..services import users_services
from fastapi import APIRouter, status, Depends, Form, HTTPException
from ..repositories import users_repository
from ..schemas.general import ErrorResponse
from ..services.Yoomoney import create_invoice, verify_webhook_signature
from core import settings, logger
import redis.asyncio as aioredis


router = APIRouter(tags = ["Users"])

@router.get("/", summary = "Get Users", status_code = status.HTTP_200_OK, response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    return await users_repository.get_users(session)

@router.post("/", summary = "Create User", status_code = status.HTTP_201_CREATED, response_model=UserRead,
             responses = {
                 409:{"model":ErrorResponse, "description": "Пользователь с таким tg_id уже существует"}
             })
async def create_user(user:UserCreate, session: AsyncSession = Depends(get_session)):
    return await users_services.create_user(user, session)

@router.get("/{tg_id}/", summary = "Get User by tg_id", status_code = status.HTTP_200_OK, response_model = UserRead,
            responses = {
                404: {"model": ErrorResponse, "description": "Пользователя не существует"}
            })
async def get_user(tg_id: int, session: AsyncSession = Depends(get_session)):
    return await users_services.get_user(tg_id, session)

@router.post("/replenisment/stars/", summary = "Создания счета на оплату звезды", status_code = status.HTTP_200_OK)
async def replenishment_balance(tg_id: int, amount: int):
    return await users_services.replenishment_balance_stars(tg_id, amount)

@router.post("/replenisment/crypto/", summary = "Создания счета на оплату криптобот", status_code = status.HTTP_200_OK)
async def replenishment_balance_cr(tg_id: int, amount: int):
    return await users_services.replenishment_balance_crypto_bot(tg_id, amount)

@router.post("/replenisment/yoomoney/", summary = "Создания счета на оплату Юмани" ,status_code = status.HTTP_200_OK)
async def replenishment_balance_yoomoney(tg_id: int, amount: int):
    return await create_invoice(tg_id, amount)

@router.post("/webhook/yoomoney/", summary="Webhook от YooMoney", status_code=status.HTTP_200_OK)
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
    session: AsyncSession = Depends(get_session)
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
        "sha1_hash": sha1_hash
    }


    logger.debug(f"[YooMoney Webhook] Received: {payload}")
    logger.debug(f"[YooMoney Webhook] Secret length: {len(settings.YOOMONEY_NOTIFICATION_SECRET)}")

    # 2. Проверка подписи
    if not verify_webhook_signature(payload, settings.YOOMONEY_NOTIFICATION_SECRET):
        logger.warn(f"[YooMoney Webhook] Signature verification FAILED")
        raise HTTPException(status_code=403, detail="Invalid signature")

    logger.debug(f"[YooMoney Webhook] Signature verification OK")

    # 3. Валидация amount
    amount_float = float(amount)
    if amount_float <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # 4. Защита от дублирования через Redis
    redis_client = aioredis.Redis(
        host=settings.DB.REDIS_HOST,
        port=settings.DB.REDIS_PORT,
        decode_responses=True
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
            raise HTTPException(status_code=500, detail=f"Failed to update balance: {str(e)}")

        await redis_client.close()
        return {"status": "ok"}

    except Exception as e:
        await redis_client.close()
        raise