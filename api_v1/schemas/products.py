from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):
    title: str
    description: str
    price: int
    rating: float
    category: str
    product_type: str

class ProductUpdateStrings(BaseModel):
    title: str|None = Field(default=None)
    description: str|None = Field(default=None)
    price: int|None = Field(default=None)
    rating: float|None = Field(default=None)
    category_title: str|None = Field(default=None)
    product_type: str|None = Field(default=None)

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class ProductUpdate(ProductUpdateStrings):
    image: str|None = Field(default=None)
    product_data: str|None = Field(default=None)


class ProductRead(BaseModel):
    id: int
    title: str
    description:str
    price: int
    category_title: str | None
    rating: float
    image: str
    product_type: str
    product_data: str | None
    model_config = ConfigDict(from_attributes=True)

class ProductReturn(BaseModel):
    id:          int
    title:       str
    description: str
    price:       int
    category:    Optional[str]

    model_config = ConfigDict(from_attributes=True)
