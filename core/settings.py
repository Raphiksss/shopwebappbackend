from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host : str = '127.0.0.52'
    port: int = '1234'

settings = Settings()

