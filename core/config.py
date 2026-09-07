from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DB_Settings(BaseSettings):
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="postgres")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str
    R2_ENDPOINT: str
    R2_PUBLIC_URL: str

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)

    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BOT_Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    admin_tg_id: str = Field(alias="ADMIN_TG_ID")
    crypto_bot_token: str = Field(alias="CRYPTO_BOT_TOKEN")
    stars_exchange_rate: float = 1.5

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


class Settings(BaseSettings):
    logging_level: str = "INFO"
    origins: List[str] = [
        "http://localhost:5173",
        "https://redstoreapp.com",
    ]
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    YOOMONEY_TOKEN: str
    YOOMONEY_WALLET: str
    YOOMONEY_NOTIFICATION_SECRET: str
    SECRET_SESSION_KEY: str
    SESSION_EXPIRE_TIME: int = 24 * 60 * 60
    SESSION_SECURE: bool = True
    DB: DB_Settings = DB_Settings()
    BOT: BOT_Settings = BOT_Settings()
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
