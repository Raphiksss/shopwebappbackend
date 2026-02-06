from sqlalchemy import Integer,BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base
from .Favorites import favorites_table


class User(Base):
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str]
    balance = mapped_column(Integer, default=0)
    favorites: Mapped[list["Product"]] = relationship(
        secondary=favorites_table,
        back_populates="fans",
        lazy="selectin",
    )

