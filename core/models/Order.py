from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Order(Base):
    user: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    sum: Mapped[int]
    status: Mapped[str] = mapped_column(default="pending")

    items: Mapped[list["OrdersItem"]] = relationship(back_populates="order")


class OrdersItem(Base):
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    order: Mapped["Order"] = relationship(back_populates="items")