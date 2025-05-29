from sqlalchemy import Column, LargeBinary, String
from sqlalchemy.orm import Mapped

from . import Base

class Product(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    data = Column(LargeBinary, nullable = False)
    mimetype = Column(String(50), nullable = False)





