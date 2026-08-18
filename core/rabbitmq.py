import logging
from faststream.rabbit import RabbitBroker, RabbitQueue
from core.config import settings

logger = logging.getLogger(__name__)

# Названия очередей
INSTANT_DELIVERY_QUEUE = "instant_delivery_queue"
ORDER_NOTIFICATIONS_QUEUE = "order_notifications_queue"
STARS_REPLENISMENT_QUEUE = "stars_replenishment_queue"
CRYPTO_BOT_REPLENISMENT_QUEUE = "crypto_bot_replenishment_queue"
DEAD_LETTER_QUEUE = "dlq_queue"

# URL для подключения к RabbitMQ
RABBITMQ_URL = f"amqp://{settings.DB.RABBITMQ_USER}:{settings.DB.RABBITMQ_PASSWORD}@{settings.DB.RABBITMQ_HOST}:{settings.DB.RABBITMQ_PORT}/"

# Создаем broker для API (producer)
broker = RabbitBroker(RABBITMQ_URL)

# Очереди с настройками
instant_delivery_queue = RabbitQueue(
    INSTANT_DELIVERY_QUEUE,
    durable=True,  # Очередь переживет перезапуск RabbitMQ
    arguments={
        "x-message-ttl": 86400000,  # 24 часа
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": DEAD_LETTER_QUEUE,
    },
)

order_notifications_queue = RabbitQueue(
    ORDER_NOTIFICATIONS_QUEUE,
    durable=True,
    arguments={
        "x-message-ttl": 3600000,  # 1 час
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": DEAD_LETTER_QUEUE,
    },
)

stars_replenisment_queue = RabbitQueue(
    STARS_REPLENISMENT_QUEUE,
    durable=True,
    arguments={
        "x-message-ttl": 3600000,  # 1 час
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": DEAD_LETTER_QUEUE,
    },
)

crypto_bot_replenisment_queue = RabbitQueue(
    CRYPTO_BOT_REPLENISMENT_QUEUE,
    durable=True,
    arguments={
        "x-message-ttl": 3600000,  # 1 час
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": DEAD_LETTER_QUEUE,
    },
)

# Dead Letter Queue для failed сообщений
dlq_queue = RabbitQueue(DEAD_LETTER_QUEUE, durable=True)


async def publish_instant_delivery(message: dict):
    try:
        await broker.publish(
            message,
            queue=instant_delivery_queue,
        )
        logger.debug(
            f"Published instant delivery message for order {message.get('order_id')}"
        )
    except Exception as e:
        logger.error(f"Failed to publish instant delivery message: {e}")
        raise


async def publish_order_notification(message: dict):
    try:
        await broker.publish(
            message,
            queue=order_notifications_queue,
        )
        logger.debug(
            f"Published order notification for order {message.get('order_id')}"
        )
    except Exception as e:
        logger.error(f"Failed to publish order notification: {e}")
        raise


async def publish_stars_replenishment(message: dict):
    try:
        await broker.publish(
            message,
            queue=stars_replenisment_queue,
        )
        logger.debug(
            f"Published replenisment stars notification for user {message.get('tg_id')}"
        )
    except Exception as e:
        logger.error(f"Failed to replenisment stars: {e}")
        raise


async def publish_crypto_bot_replenishment(message: dict):
    try:
        await broker.publish(
            message,
            queue=crypto_bot_replenisment_queue,
        )
        logger.debug(
            f"Published replenisment stars notification for user {message.get('tg_id')}"
        )
    except Exception as e:
        logger.error(f"Failed to replenisment stars: {e}")
        raise
