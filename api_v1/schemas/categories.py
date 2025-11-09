from pydantic import BaseModel

class CategoryRead(BaseModel):
    id: int
    title: str
    img: str