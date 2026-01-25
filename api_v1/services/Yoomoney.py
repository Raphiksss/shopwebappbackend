import time
import hashlib
from yoomoney import Quickpay
from core import settings
from core.common import logger

YOOMONEY_TOKEN = settings.YOOMONEY_TOKEN
YOOMONEY_WALLET = settings.YOOMONEY_WALLET

async def create_invoice(tg_id:int, amount:int):
    label = f"order_{tg_id}_{int(time.time())}"

    quickpay = Quickpay(
        receiver=YOOMONEY_WALLET,
        quickpay_form="shop",
        targets="Оплата товара",
        paymentType="AC",
        sum=amount,
        label=label
    )
    payment_url = quickpay.base_url
    return {
        "payment_url": payment_url,
        "label": label
    }

def verify_webhook_signature(payload: dict, notification_secret: str) -> bool:
    """Проверка подлинности webhook через SHA-1"""
    signature_string = (
        f"{payload['notification_type']}&"
        f"{payload['operation_id']}&"
        f"{payload['amount']}&"
        f"{payload['currency']}&"
        f"{payload['datetime']}&"
        f"{payload['sender']}&"
        f"{payload['codepro']}&"
        f"{notification_secret}&"
        f"{payload['label']}"
    )
    computed_hash = hashlib.sha1(signature_string.encode('utf-8')).hexdigest()


    logger.debug(f"[Signature] String: {signature_string}",)
    logger.debug(f"[Signature] Computed: {computed_hash}")
    logger.debug(f"[Signature] Received: {payload['sha1_hash']}")

    return computed_hash == payload['sha1_hash']
