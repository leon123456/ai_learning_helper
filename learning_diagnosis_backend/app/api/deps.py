# app/api/deps.py
from functools import lru_cache
from app.services.llm import LLMClient
from app.core.config import settings

@lru_cache()
def get_llm_client() -> LLMClient:
    return LLMClient(api_key=settings.OPENAI_API_KEY)
