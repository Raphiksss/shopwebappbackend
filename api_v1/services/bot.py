from faststream.rabbit.fastapi import RabbitRouter
from core.config import settings

rabbitmq_url = f"amqp://{settings.DB.RABBITMQ_USER}:{settings.DB.RABBITMQ_PASSWORD}@{settings.DB.RABBITMQ_HOST}:{settings.DB.RABBITMQ_PORT}/"

rabbits_router = RabbitRouter(rabbitmq_url)

@rabbits_router.post("/orders/new/")
async def order_create(tg_id: int):
    await rabbits_router.broker.publish(f"Новый заказ от пользователя {tg_id}")
    return {"status": "order created"}

