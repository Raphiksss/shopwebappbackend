from pydantic import BaseModel

class AssentColor(BaseModel):
    color: str

class StarsExchangeRate(BaseModel):
    exchange_rate: float

class BotToken(BaseModel):
    bot_token: str

class CryptoBotToken(BaseModel):
    crypto_bot_token: str

class YooMoneyData(BaseModel):
    token: str
    wallet: str
    notification_secret: str

class PaymentMethods(BaseModel):
    stars: bool
    crypto_bot:bool
    yoomoney:bool