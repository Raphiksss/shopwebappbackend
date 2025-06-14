from pydantic import BaseModel


class UserCreate(BaseModel):
    tg_id: int
    balance: int
    username: str