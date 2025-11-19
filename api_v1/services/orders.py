import asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.models.Order import OrdersItem
from ..schemas.orders import CreateOrder
from ..services import products,users,cart
from ..repositories import orders
from core.models import Order



async def create_order(tg_id: int, session: AsyncSession):
    #создаем переменные на будущее и вытаскиваем пользователя с корзиной
    sum = 0
    items:dict = {}
    products_ids = []
    user = await users.get_user(tg_id, session)
    cart_products = cart.get_card(tg_id)

    #получаем айдишники товаров с редиса, названия и считаем сумму
    for key, value in cart_products["products"].items():
        res = await products.get_product(key, session)
        print(key)
        products_ids.append(key)
        sum += res.price * value
        items[res.title] = value
    #вычитаем деньги
    if user.balance >= sum:
        user.balance -= sum
        await session.commit()
    else:
        raise HTTPException(500)
    print(items)
    #создаем заказ
    new_order = Order(user=tg_id, sum=sum)
    await orders.create_order(new_order, session)
    await session.flush()

    #добовляем в него товары
    for product_id in products_ids:
        item = OrdersItem(order_id=new_order.id, product_id=product_id)
        session.add(item)
    await session.commit()
    await session.refresh(new_order)

    cart.del_all_card(tg_id)

    #выводим сообщения в боте
    from bot.bot import include_order
    # try:
    asyncio.create_task(
            include_order(tg_id=new_order.user, order_id=new_order.id, items=items, username = user.username, sum = new_order.sum)
        )

    return new_order