from pydantic import BaseModel, Field, ConfigDict
from ..schemas.users import UserRead
from ..schemas.products import ProductRead


class CreateOrder(BaseModel):
    tg_id: int
    # product_ids: list[int]


class OrderItems(BaseModel):
    id: int
    product_id: int
    product_rel: ProductRead


class ReadOrders(BaseModel):
    id: int
    status: str
    sum: int
    user_rel: UserRead
    items: list[OrderItems]

    model_config = ConfigDict(from_attributes=True)


class PartialOrderUpdate(BaseModel):
    user: int | None = Field(None)
    sum: str | None = Field(None)
    status: str | None = Field(None)
