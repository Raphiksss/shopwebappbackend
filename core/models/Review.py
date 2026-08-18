from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
from .Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Product import Product


class Review(Base):
    body: Mapped[str]
    rate: Mapped[float]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="reviews")
