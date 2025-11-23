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
            # 支持多个 Azure 部署
            # 优先使用旧配置（向后兼容）
            if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
                self.client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                )
                self.deployment = settings.AZURE_OPENAI_DEPLOYMENT
                self.azure_deployments = {}  # 不使用多部署模式
            else:
                # 使用新的多部署配置
                self._init_azure_deployments()
                # 设置默认部署
                default_deployment = settings.AZURE_DEFAULT_DEPLOYMENT.lower()
                if default_deployment == "gpt51":
                    self.client = self.azure_deployments["gpt51"]["client"]
                    self.deployment = settings.AZURE_OPENAI_DEPLOYMENT_GPT51
                else:  # 默认使用 gpt4o2
                    self.client = self.azure_deployments["gpt4o2"]["client"]
                    self.deployment = settings.AZURE_OPENAI_DEPLOYMENT_GPT4O2

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
    
    def _init_azure_deployments(self):
        """初始化多个 Azure 部署的客户端"""
        self.azure_deployments = {}
        
        # gpt-4o-2 部署
        if settings.AZURE_OPENAI_ENDPOINT_GPT4O2 and settings.AZURE_OPENAI_API_KEY_GPT4O2:
            self.azure_deployments["gpt4o2"] = {
                "client": AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY_GPT4O2,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT_GPT4O2,
                ),
                "deployment": settings.AZURE_OPENAI_DEPLOYMENT_GPT4O2,
            }
        
        # gpt-5.1 部署
        if settings.AZURE_OPENAI_ENDPOINT_GPT51 and settings.AZURE_OPENAI_API_KEY_GPT51:
            self.azure_deployments["gpt51"] = {
                "client": AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY_GPT51,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT_GPT51,
                ),
                "deployment": settings.AZURE_OPENAI_DEPLOYMENT_GPT51,
            }
        
        if not self.azure_deployments:
            raise ValueError("至少需要配置一个 Azure 部署")
    
    def _get_azure_client(self, model: Optional[str] = None):
        """根据 model 参数选择对应的 Azure 客户端"""
        # 如果使用旧配置，直接返回
        if not hasattr(self, 'azure_deployments') or not self.azure_deployments:
            return self.client, self.deployment
        
        # 根据 model 参数选择部署
        if model:
            model_lower = model.lower()
            if "gpt-5.1" in model_lower or "gpt51" in model_lower:
                if "gpt51" in self.azure_deployments:
                    return self.azure_deployments["gpt51"]["client"], self.azure_deployments["gpt51"]["deployment"]
            elif "gpt-4o-2" in model_lower or "gpt4o2" in model_lower:
                if "gpt4o2" in self.azure_deployments:
                    return self.azure_deployments["gpt4o2"]["client"], self.azure_deployments["gpt4o2"]["deployment"]
        
        # 默认使用当前配置的客户端
        return self.client, self.deployment

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
            # 根据 model 参数选择对应的 Azure 客户端
            client, deployment = self._get_azure_client(model)
            
            # gpt-5.1 只支持 temperature=1.0（默认值），不支持其他值
            if model and ("gpt-5.1" in model.lower() or "gpt51" in model.lower()):
                if temperature != 1.0:
                    temperature = 1.0  # gpt-5.1 只支持默认值 1.0
            elif not model and hasattr(self, 'deployment') and "gpt-5.1" in self.deployment.lower():
                # 使用默认部署且是 gpt-5.1
                if temperature != 1.0:
                    temperature = 1.0  # gpt-5.1 只支持默认值 1.0
            
            response = client.chat.completions.create(
                model=deployment,
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
                timeout=120,  # 增加到 120 秒
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
            res = await client.post(self.qwen_url, headers=headers, json=payload, timeout=120)  # 增加到 120 秒
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
            # 如果使用多部署模式，返回默认部署名称
            if hasattr(self, 'azure_deployments') and self.azure_deployments:
                default_deployment = settings.AZURE_DEFAULT_DEPLOYMENT.lower()
                if default_deployment == "gpt51":
                    return settings.AZURE_OPENAI_DEPLOYMENT_GPT51
                else:
                    return settings.AZURE_OPENAI_DEPLOYMENT_GPT4O2
            # 向后兼容旧配置
            return settings.AZURE_OPENAI_DEPLOYMENT or "gpt-4o-2"
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
        model: Optional[str] = None,
    ) -> str:
        """
        使用带图片的对话模型（如 Azure gpt-4o）做 OCR。
        目前支持 provider: azure / openai。
        
        Args:
            prompt: 提示词
            image_url: 图片 URL
            image_base64: 图片 base64 编码
            temperature: 温度参数
            model: 指定使用的模型（可选）
                   - 对于 Azure: "gpt-4o-2", "gpt4o2", "gpt-5.1-chat", "gpt51" 或 None（使用配置的默认值）
        
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
            # 根据配置或参数选择 OCR 部署
            if model:
                # 使用指定的模型
                ocr_model = model
            else:
                # 使用配置的 OCR 部署
                ocr_deployment = settings.AZURE_OCR_DEPLOYMENT.lower()
                if ocr_deployment == "gpt51":
                    ocr_model = "gpt-5.1-chat"
                elif ocr_deployment == "auto":
                    # auto 模式：优先尝试 gpt4o2
                    ocr_model = "gpt-4o-2"
                else:  # 默认使用 gpt4o2
                    ocr_model = "gpt-4o-2"
            
            client, deployment = self._get_azure_client(ocr_model)
            
            # gpt-5.1 只支持 temperature=1.0（默认值），不支持其他值
            if "gpt-5.1" in ocr_model.lower() or "gpt51" in ocr_model.lower():
                if temperature != 1.0:
                    temperature = 1.0  # gpt-5.1 只支持默认值 1.0
            
            try:
                response = client.chat.completions.create(
                    model=deployment,
                    messages=messages,
                    temperature=temperature,
                )
            except Exception as e:
                # 如果使用 auto 模式且 gpt4o2 失败，尝试 gpt51
                if settings.AZURE_OCR_DEPLOYMENT.lower() == "auto" and "gpt-4o-2" in ocr_model.lower():
                    if hasattr(self, 'azure_deployments') and self.azure_deployments and "gpt51" in self.azure_deployments:
                        client, deployment = self._get_azure_client("gpt-5.1-chat")
                        response = client.chat.completions.create(
                            model=deployment,
                messages=messages,
                temperature=temperature,
            )
                    else:
                        raise e
                else:
                    raise e
        else:
            # openai 官方路径（如果以后用到）
            response = self.client.chat.completions.create(
                model=model or self._get_default_model(),
                messages=messages,
                temperature=temperature,
            )

        return response.choices[0].message.content

