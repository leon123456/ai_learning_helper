# app/api/deps.py

from functools import lru_cache
from app.services.llm import LLMClient
from fastapi import HTTPException

@lru_cache()
def get_llm_client() -> LLMClient:
    try:
        return LLMClient()
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"LLM 客户端初始化失败: {error_msg}. 请检查 .env 配置文件。"
        )
