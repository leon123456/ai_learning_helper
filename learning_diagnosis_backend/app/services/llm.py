# app/services/llm.py

from typing import List, Dict, Optional, Literal
from app.core.config import settings
import json

# --- Providers ---
from openai import OpenAI, AzureOpenAI
import httpx


class LLMClient:
    """
    统一大模型适配层：支持 Azure / OpenAI / DeepSeek / Qwen（DashScope）
    """

    def __init__(self):
        self.provider = settings.PROVIDER.lower()

        if self.provider == "azure":
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            )
            self.deployment = settings.AZURE_OPENAI_DEPLOYMENT

        elif self.provider == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        elif self.provider == "deepseek":
            self.deepseek_key = settings.DEEPSEEK_API_KEY
            self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"

        elif self.provider == "qwen":
            self.qwen_key = settings.DASH_SCOPE_API_KEY
            self.qwen_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        else:
            raise ValueError("Unsupported LLM Provider")

    # -------------------------- Core Chat -----------------------------
    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        response_format: Optional[Literal["json"]] = None,
        temperature: float = 0.2,
    ) -> str:

        model = model or self._get_default_model()

        if self.provider in ["azure", "openai"]:
            return self._chat_openai(system_prompt, user_message, model, response_format, temperature)

        elif self.provider == "deepseek":
            return await self._chat_deepseek(system_prompt, user_message, model, response_format, temperature)

        elif self.provider == "qwen":
            return await self._chat_qwen(system_prompt, user_message, model, response_format, temperature)

        raise ValueError("Invalid provider")

    # ------------------------ OpenAI/Azure ---------------------------
    def _chat_openai(self, system_prompt, user_message, model, response_format, temperature):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        if self.provider == "azure":
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"} if response_format == "json" else None,
            )
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"} if response_format == "json" else None,
            )

        return response.choices[0].message.content

    # -------------------------- DeepSeek -----------------------------
    async def _chat_deepseek(self, system_prompt, user_message, model, response_format, temperature):
        payload = {
            "model": model or "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(
                self.deepseek_url,
                headers={"Authorization": f"Bearer {self.deepseek_key}"},
                json=payload,
                timeout=30,
            )
            res = res.json()
            return res["choices"][0]["message"]["content"]

    # --------------------------- Qwen --------------------------------
    async def _chat_qwen(self, system_prompt, user_message, model, response_format, temperature):
        payload = {
            "model": model or "qwen-max",
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {self.qwen_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(self.qwen_url, headers=headers, json=payload, timeout=30)
            obj = res.json()

            return obj["output"]["text"]

    # -------------------------- JSON Helper ----------------------------
    async def chat_json(self, system_prompt: str, user_message: str, model: str = None):
        text = await self.chat(system_prompt, user_message, model, response_format="json")
        try:
            return json.loads(text)
        except Exception:
            return {"error": "JSON 解析失败", "raw": text}

    # -------------------------- Utilities ------------------------------
    def _get_default_model(self):
        if self.provider == "azure":
            return settings.AZURE_OPENAI_DEPLOYMENT
        if self.provider == "openai":
            return "gpt-4.1-mini"
        if self.provider == "deepseek":
            return "deepseek-chat"
        if self.provider == "qwen":
            return "qwen-max"
    
    async def ocr_with_image(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        temperature: float = 0.0,
    ) -> str:
        """
        使用带图片的对话模型（如 Azure gpt-4o）做 OCR。
        目前支持 provider: azure / openai。
        返回：模型生成的纯文本（题目内容）。
        """
        if not image_url and not image_base64:
            raise ValueError("image_url 或 image_base64 必须提供一个")

        if self.provider not in ["azure", "openai"]:
            raise ValueError("ocr_with_image 目前只支持 azure / openai provider")

        if image_url:
            img_url = image_url
        else:
            # 注意前缀
            img_url = f"data:image/png;base64,{image_base64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        },
                    },
                ],
            }
        ]

        if self.provider == "azure":
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
            )
        else:
            # openai 官方路径（如果以后用到）
            response = self.client.chat.completions.create(
                model=self._get_default_model(),
                messages=messages,
                temperature=temperature,
            )

        return response.choices[0].message.content

