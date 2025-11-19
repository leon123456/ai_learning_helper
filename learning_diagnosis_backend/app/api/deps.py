# app/api/deps.py

from functools import lru_cache
from app.services.llm import LLMClient

@lru_cache()
def get_llm_client() -> LLMClient:
    return LLMClient()
