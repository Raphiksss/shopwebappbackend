from typing import Optional

from pydantic import BaseModel,ConfigDict
from sqlalchemy import Column, LargeBinary



class ProductCreate(BaseModel):
    title: str
    subtitle: str
    description: str
    price: int
    rating: float
    category: str | None


class ProductRead(BaseModel):
    id: int
    title: str
    subtitle: str
    description:str
    price: int
    image: str
    rating: float
    category: str | None
    model_config = ConfigDict(from_attributes=True)

class ProductUpdatePartial(BaseModel):
    title: str | None
    description: str | None
    price: int | None
    category: str | None


class ProductReturn(BaseModel):
    id:          int
    title:       str
    description: str
    price:       int
    category:    Optional[str]

    model_config = ConfigDict(from_attributes=True)




