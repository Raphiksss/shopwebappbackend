from pydantic import BaseModel, Field


class CreateOrder(BaseModel):
    tg_id: int
    # product_ids: list[int]

class PartialOrderUpdate(BaseModel):
    user: int | None = Field(None)
    sum: str | None = Field(None)
    status: str | None = Field(None)