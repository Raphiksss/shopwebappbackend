from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Users import User
    from .Product import Product

class Order(Base):
    user: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    sum: Mapped[int]
    status: Mapped[str] = mapped_column(default="pending")

    items: Mapped[list["OrdersItem"]] = relationship(back_populates="order")
    user_rel:Mapped["User"] = relationship(back_populates="orders")


class OrdersItem(Base):
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product_rel: Mapped["Product"] = relationship(back_populates="in_order")

    order: Mapped["Order"] = relationship(back_populates="items")