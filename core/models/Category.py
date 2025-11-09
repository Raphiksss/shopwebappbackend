from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Product import Product


class Category(Base):
    title: Mapped[str] = mapped_column(unique=True)
    img: Mapped[str]
    products: Mapped[list["Product"]] = relationship(back_populates = "category")
