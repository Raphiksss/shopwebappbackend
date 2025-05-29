from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    host : str = '127.0.0.52'
    port: int = '1234'
    db_url: str = 'sqlite+aiosqlite:///./db.sqlite3'

settings = Settings()

