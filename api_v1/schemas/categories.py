from pydantic import BaseModel, Field, field_validator


class CategoryRead(BaseModel):
    id: int
    title: str
    img: str

class CategoryPartialUpdate(BaseModel):
    title: str|None = Field(None)
    img: str|None = Field(None)

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v