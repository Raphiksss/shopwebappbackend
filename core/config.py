from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DB_Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://postgres:password123@postgresql:5432/postgres"

    R2_ACCESS_KEY: str = Field("", validation_alias="R2_ACCESS_KEY")
    R2_SECRET_KEY: str = Field("", validation_alias="R2_SECRET_KEY")
    R2_ENDPOINT: str = Field("", validation_alias="R2_ENDPOINT")
    R2_PUBLIC_URL: str = Field("", validation_alias="R2_PUBLIC_URL")

    REDIS_HOST: str = Field("localhost", validation_alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, validation_alias="REDIS_PORT")

    RABBITMQ_HOST: str = Field("localhost", validation_alias="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(5672, validation_alias="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field("admin", validation_alias="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field("admin123", validation_alias="RABBITMQ_PASSWORD")

    model_config = SettingsConfigDict(extra="ignore")


class BOT_Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    admin_tg_id: str = Field(alias="ADMIN_TG_ID")
    crypto_bot_token: str = Field(alias="CRYPTO_BOT_TOKEN")
    stars_exchange_rate: float = 1.5

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


class Settings(BaseSettings):
    host: str = "localhost"
    port: int = 8000
    logging_level: str = "INFO"
    origins: List[str] = [
        "http://localhost:5173",
        "http://10.177.93.85:5173",
        "https://redstoreapp.com",
    ]
    ADMIN_USERNAME: str = Field(alias="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(alias="ADMIN_PASSWORD")
    YOOMONEY_TOKEN: str = Field(alias="YOOMONEY_TOKEN")
    YOOMONEY_WALLET: str = Field(alias="YOOMONEY_WALLET")
    YOOMONEY_NOTIFICATION_SECRET: str = Field(alias="YOOMONEY_NOTIFICATION_SECRET")
    SECRET_SESSION_KEY: str = Field(alias="SECRET_SESSION_KEY")
    SESSION_EXPIRE_TIME: int = 24 * 60 * 60
    SESSION_SECURE: bool = True
    DB: DB_Settings = DB_Settings()
    BOT: BOT_Settings = BOT_Settings()
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
