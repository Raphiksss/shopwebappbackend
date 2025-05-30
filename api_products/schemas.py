from pydantic import BaseModel,ConfigDict
from sqlalchemy import Column, LargeBinary



class ProductCreate(BaseModel):
    title: str
    description: str
    price: int
    category: str | None

class ProductRead(BaseModel):
    id: int
    title: str
    description:str
    price: int
    image_b64: str

    model_config = ConfigDict(from_attributes=True)

