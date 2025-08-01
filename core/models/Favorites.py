from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import mapped_column
from .Base import Base

favorites_table = Table(
    "favorites",
    Base.metadata,
    Column("user_id",    Integer, ForeignKey("users.id"),    primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)
