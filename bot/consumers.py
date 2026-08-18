import logging
from faststream.rabbit import RabbitBroker
from core.rabbitmq import (
    RABBITMQ_URL,
    instant_delivery_queue,
    order_notifications_queue,
    stars_replenisment_queue,
    crypto_bot_replenisment_queue,
)
from api_v1.schemas.messages import InstantDeliveryMessage, OrderNotificationMessage
from bot.bot import give_a_product, include_order, stars_buying, crypto_replenishment

logger = logging.getLogger(__name__)

# Создаем отдельный broker для consumers
# Retry механизм: при возникновении ошибки (raise Exception) сообщение
# автоматически переотправляется RabbitMQ (nack). После нескольких неудачных
# попыток сообщение отправляется в Dead Letter Queue (DLQ)
consumer_broker = RabbitBroker(RABBITMQ_URL)


@consumer_broker.subscriber(
    queue=instant_delivery_queue,
)
async def handle_instant_delivery(message: InstantDeliveryMessage):
    try:
        logger.debug(
            f"Processing instant delivery for order {message.order_id}, user {message.tg_id}"
        )

        await give_a_product(
            tg_id=message.tg_id,
            product_title=message.product_title,
            product_data=message.product_data,
        )

        logger.info(
            f"Successfully delivered product '{message.product_title}' to user {message.tg_id}"
        )

    except Exception as e:
        logger.error(
            f"Failed to deliver product for order {message.order_id}: {e}",
            exc_info=True,
        )
        # Пробрасываем исключение - RabbitMQ автоматически переотправит сообщение (nack)
        # После нескольких попыток сообщение попадет в DLQ
        raise


@consumer_broker.subscriber(
    queue=order_notifications_queue,
)
async def handle_order_notification(message: OrderNotificationMessage):
    try:
        logger.debug(
            f"Processing order notification for order {message.order_id}, user {message.tg_id}"
        )

        await include_order(
            tg_id=message.tg_id,
            username=message.username,
            order_id=message.order_id,
            items=message.items,
            sum=message.sum,
        )

        logger.info(
            f"Successfully sent order notification for order {message.order_id}"
        )

    except Exception as e:
        logger.error(
            f"Failed to send notification for order {message.order_id}: {e}",
            exc_info=True,
        )
        # Пробрасываем исключение - RabbitMQ автоматически переотправит сообщение (nack)
        # После нескольких попыток сообщение попадет в DLQ
        raise


@consumer_broker.subscriber(queue=stars_replenisment_queue)
async def handle_stars_replenishment(message: dict):
    try:
        tg_id = message.get("tg_id")
        amount = message.get("amount")
        logger.debug(
            f"Processing stars replenishment for user {tg_id}, amount {amount}"
        )

        await stars_buying(tg_id, amount)

        logger.info(f"Successfully replenished {amount} stars for user {tg_id}")
    except Exception as e:
        logger.error(f"Failed to replenish stars for user {tg_id}: {e}", exc_info=True)
        # Пробрасываем исключение - RabbitMQ автоматически переотправит сообщение (nack)
        # После нескольких попыток сообщение попадет в DLQ
        raise


@consumer_broker.subscriber(queue=crypto_bot_replenisment_queue)
async def handle_crypto_bot_replenishment(message: dict):
    try:
        tg_id = message.get("tg_id")
        amount = message.get("amount")
        logger.debug(
            f"Processing ccrypto_bot replenishment for user {tg_id}, amount {amount}"
        )

        await crypto_replenishment(tg_id, amount)

        logger.info(f"Successfully replenished {amount} crypto_bot for user {tg_id}")
    except Exception as e:
        logger.error(
            f"Failed to replenish crypto_bot for user {tg_id}: {e}", exc_info=True
        )
        # Пробрасываем исключение - RabbitMQ автоматически переотправит сообщение (nack)
        # После нескольких попыток сообщение попадет в DLQ
        raise


async def start_consumers():
    """Запускает всех consumers для обработки сообщений"""
    logger.info("Starting RabbitMQ consumers...")
    await consumer_broker.start()
    logger.info("RabbitMQ consumers started successfully")


async def stop_consumers():
    """Останавливает всех consumers"""
    logger.info("Stopping RabbitMQ consumers...")
    await consumer_broker.close()
    logger.info("RabbitMQ consumers stopped")
