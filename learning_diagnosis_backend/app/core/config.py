# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"
    OPENAI_API_KEY: str = ""
    # 后面可以加 DB_URL、REDIS_URL 等

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
