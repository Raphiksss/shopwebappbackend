from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base

class User(Base):
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[str]
    balance = mapped_column(Integer, default=0)

