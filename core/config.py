from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    host : str = '127.0.0.2'
    port: int = '8000'
    db_url: str = 'sqlite+aiosqlite:///./db.sqlite3'

settings = Settings()

