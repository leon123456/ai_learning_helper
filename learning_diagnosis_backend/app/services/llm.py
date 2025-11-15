# app/services/llm.py
from typing import List, Dict, Any

class LLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: 在这里初始化真正的 LLM SDK 客户端

    async def chat(
        self, 
        system_prompt: str, 
        messages: List[Dict[str, str]],
        model: str = "gpt-4.1-mini"
    ) -> str:
        """
        通用对话接口：
        messages: [{"role": "user"/"assistant"/"system", "content": "..."}]
        """
        # TODO: 调用真实 LLM，这里先返回 mock
        return "（LLM 未真正接入，这里是一个占位回复）"
