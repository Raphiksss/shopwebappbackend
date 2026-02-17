from pydantic import BaseModel, ConfigDict,Field


class UserCreate(BaseModel):
    username: str
    tg_id: int

class UserRead(BaseModel):
    id:int
    username: str
    balance: int
    tg_id: int

    model_config = ConfigDict(from_attributes=True)

class UserPartialUpdate(BaseModel):
    username:str|None = Field(default = None)
    balance: int| None = Field(default = None)

    model_config = ConfigDict(from_attributes=True)

class YooMoneyWebhookPayload(BaseModel):
    """Входящее уведомление от YooMoney"""
    notification_type: str
    operation_id: str
    amount: float
    withdraw_amount: float
    currency: str
    datetime: str
    sender: str = ""
    codepro: bool
    label: str
    sha1_hash: str
    unaccepted: bool = False