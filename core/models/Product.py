from sqlalchemy import LargeBinary, String, Column
from sqlalchemy.orm import Mapped
from .Base import Base

class Product(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    data: Mapped[bytes] = Column(LargeBinary, nullable=False)
    mimetype: Mapped[str] = Column(String(50), nullable=False)


