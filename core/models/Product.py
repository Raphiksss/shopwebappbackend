from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Enum

from .Users import User
from .Base import Base
from .Favorites import favorites_table
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Review import Review
    from .Category import Category
    from .Order import OrdersItem


class Product(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    category_title: Mapped[str] = mapped_column(
        ForeignKey("categorys.title", onupdate="CASCADE"), nullable=True
    )
    image: Mapped[str]
    rating: Mapped[float]
    fans: Mapped[list[User]] = relationship(
        secondary=favorites_table,
        back_populates="favorites",
        lazy="selectin",
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")
    category: Mapped["Category"] = relationship(back_populates="products")
    product_type: Mapped[str] = mapped_column(
        Enum("instantly", "notinstantly", name="processing_mode"),
        server_default="notinstantly",
    )
    product_data: Mapped[str | None] = mapped_column(server_default=None, nullable=True)
    in_order: Mapped[list["OrdersItem"]] = relationship(back_populates="product_rel")
