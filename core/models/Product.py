from sqlalchemy import LargeBinary, String, Column
from sqlalchemy.orm import Mapped
from .Base import Base

class Product(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    category: Mapped[str | None]
    image: Mapped[str]
    subtitle: Mapped[str]
    rating: Mapped[float]






