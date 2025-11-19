from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DB_Settings(BaseSettings):
    db_url: str = 'sqlite+aiosqlite:///./db.sqlite3'

    MINIO_ROOT_USER:str  = Field('admin',  validation_alias = 'MINIO_ROOT_USER')
    MINIO_ROOT_PASSWORD:str  = Field('secret123',  validation_alias = 'MINIO_ROOT_PASSWORD')
    MINIO_HOST:str  = Field('localhost',  validation_alias = 'MINIO_HOST' )
    MINIO_PORT:int  = Field(9000,  validation_alias = 'MINIO_PORT' )

    REDIS_HOST: str = Field('localhost', validation_alias = 'REDIS_HOST')
    REDIS_PORT:int = Field(6379, validation_alias = 'REDIS_PORT' )

    model_config = SettingsConfigDict(extra='ignore')

class BOT_Settings(BaseSettings):
    bot_token: str = Field(alias = 'BOT_TOKEN')
    admin_tg_id: str = Field(alias = 'ADMIN_TG_ID')

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')

class Settings(BaseSettings):
    host : str = 'localhost'
    port: int = 8000
    logging_level: str = 'ERROR'
    origins: List[str] = ["http://localhost:5173", "http://10.177.93.85:5173"]
    DB: DB_Settings = DB_Settings()
    BOT: BOT_Settings = BOT_Settings()
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')


settings = Settings()

