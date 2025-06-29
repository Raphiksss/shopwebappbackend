from typing import List
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    host : str = '127.0.0.2'
    port: int = '8000'
    db_url: str = 'sqlite+aiosqlite:///./db.sqlite3'
    logging_level: str = 'INFO'
    bot_token: str = "7971991234:AAEGi3z3rpEcmzMI8PN3HQJtC0j7ipY-rHk"
    origins: List[str] = ["http://localhost:5173"]

settings = Settings()

