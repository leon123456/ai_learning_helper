# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROVIDER: str = "azure"     # azure | openai | deepseek | qwen

    # OpenAI 官方
    OPENAI_API_KEY: str = ""

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-11-20"
    AZURE_OPENAI_DEPLOYMENT: str = ""

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""

    # Qwen / DashScope
    DASH_SCOPE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
