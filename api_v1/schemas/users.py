from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    tg_id: int
    balance: int

class UserRead(BaseModel):
    username: str
    balance: int
    tg_id: int
    model_config = ConfigDict(from_attributes=True)