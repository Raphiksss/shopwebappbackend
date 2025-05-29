from pydantic import BaseModel,ConfigDict
from sqlalchemy import Column, LargeBinary



class ProductCreate(BaseModel):
    title: str
    description: str
    price: int

class ProductRead(BaseModel):
    id: int
    title: str
    description:str
    price: int

