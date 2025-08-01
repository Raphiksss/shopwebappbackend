from sqlalchemy.orm import Mapped, relationship
from .Users import User
from .Base import Base
from .Favorites import favorites_table


class Product(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    category: Mapped[str | None]
    image: Mapped[str]
    subtitle: Mapped[str]
    rating: Mapped[float]
    fans: Mapped[list[User]] = relationship(
        secondary=favorites_table,
        back_populates="favorites",
        lazy="selectin",
    )






