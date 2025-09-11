from typing import Optional
from pydantic import BaseModel,ConfigDict



class ProductCreate(BaseModel):
    title: str
    description: str
    price: int
    rating: float
    category: str | None


class ProductRead(BaseModel):
    id: int
    title: str
    description:str
    price: int
    category: str | None
    rating: float
    image: str
    model_config = ConfigDict(from_attributes=True)

class ProductReturn(BaseModel):
    id:          int
    title:       str
    description: str
    price:       int
    category:    Optional[str]

    model_config = ConfigDict(from_attributes=True)
