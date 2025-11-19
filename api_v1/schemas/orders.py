from pydantic import BaseModel

class CreateOrder(BaseModel):
    tg_id: int
    # product_ids: list[int]