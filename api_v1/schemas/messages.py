from pydantic import BaseModel, Field


class InstantDeliveryMessage(BaseModel):
    """Сообщение для мгновенной доставки цифрового товара"""
    tg_id: int = Field(..., description="Telegram ID пользователя")
    product_title: str = Field(..., description="Название товара")
    product_data: str = Field(..., description="Путь к файлу товара")
    order_id: int = Field(..., description="ID заказа")


class OrderNotificationMessage(BaseModel):
    """Сообщение для уведомления о заказе"""
    tg_id: int = Field(..., description="Telegram ID пользователя")
    username: str = Field(..., description="Username пользователя")
    order_id: int = Field(..., description="ID заказа")
    items: dict[str, int] = Field(..., description="Товары в заказе {название: количество}")
    sum: int = Field(..., description="Сумма заказа")

class ReplenismentMessage(BaseModel):
    """Сообщение для пополнения баланса звёзд"""
    tg_id: int = Field(..., description="Telegram ID пользователя")
    amount: int = Field(..., description="Сумма пополнения")