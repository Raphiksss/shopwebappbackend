import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.models.Order import OrdersItem
from ..schemas.orders import CreateOrder
from ..services import products, users, cart
from ..repositories import orders
from core.models import Order
from core.rabbitmq import publish_instant_delivery, publish_order_notification
from ..schemas.products import ProductRead
from ..schemas.messages import InstantDeliveryMessage, OrderNotificationMessage
from ..schemas.orders import PartialOrderUpdate

logger = logging.getLogger(__name__)


async def create_order(tg_id: int, session: AsyncSession):
    # создаем переменные на будущее и вытаскиваем пользователя с корзиной
    sum = 0

    user = await users.get_user(tg_id, session)
    user_cart = cart.get_card(tg_id)
    items = user_cart["products"].items()
    all_prods: list[tuple[int, ProductRead]] = []
    product_titles: dict[str, int] = {}
    # есть ли в заказе товары которые не выдаются моментально
    nt_i = False
    instant_products = []  # Список товаров для мгновенной доставки

    for key, value in items:
        res = await products.get_product(int(key), session)
        all_prods.append((value, res))
        product_titles[res.title] = value
        sum += res.price * value
        if res.product_type == "instantly":
            # Сохраняем товар для отправки через RabbitMQ после создания заказа
            instant_products.append(
                {"product_title": res.title, "product_data": res.product_data}
            )
        else:
            nt_i = True
    # вычитаем деньги
    if user.balance >= sum:
        user.balance -= sum
        await session.commit()
    else:
        raise HTTPException(500)

    # создаем заказ
    new_order = Order(user=tg_id, sum=sum)
    await orders.create_order(new_order, session)
    await session.flush()

    # добовляем в него товары
    for quantity, prod in all_prods:
        session.add(
            OrdersItem(
                order_id=new_order.id,
                product_id=prod.id,
                title=prod.title,
                price=prod.price,
                quantity=quantity,
            )
        )

    await session.commit()
    await session.refresh(new_order)

    cart.del_all_card(tg_id)

    for product in instant_products:
        message = InstantDeliveryMessage(
            tg_id=tg_id,
            product_title=product["product_title"],
            product_data=product["product_data"],
            order_id=new_order.id,
        )
        await publish_instant_delivery(message.model_dump())
        logger.info(
            f"Published instant delivery for product '{product['product_title']}' in order {new_order.id}"
        )

    if nt_i:
        notification = OrderNotificationMessage(
            tg_id=new_order.user,
            username=user.username,
            order_id=new_order.id,
            items=product_titles,
            sum=new_order.sum,
        )
        await publish_order_notification(notification.model_dump())
        logger.info(f"Published order notification for order {new_order.id}")

    return new_order


async def get_orders(
    filter_by_status: str | None,
    page: int | None,
    limit: int | None,
    session: AsyncSession,
):
    res = await orders.get_orders(session, filter_by_status, page, limit)
    return list(res)


async def product_partial_update(
    order_id: int, new_order: PartialOrderUpdate, session: AsyncSession
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(404, detail="Order not found")
    return await orders.partial_order_update(order, new_order, session)
