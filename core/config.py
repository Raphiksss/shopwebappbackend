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

class Settings(BaseSettings):
    host : str = '127.0.0.2'
    port: int = 8000
    logging_level: str = 'ERROR'
    bot_token: str = Field(validation_alias = 'BOT_TOKEN')
    origins: List[str] = ["http://localhost:5173"]
    DB: DB_Settings = DB_Settings()

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

