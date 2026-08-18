from sqlalchemy import ForeignKey, Table, Column, Integer, BigInteger
from .Base import Base

favorites_table = Table(
    "favorites",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)
