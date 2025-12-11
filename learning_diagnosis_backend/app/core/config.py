# app/core/config.py
from pathlib import Path
from pydantic_settings import BaseSettings

# 获取项目根目录（config.py 所在目录的上两级）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    PROVIDER: str = "azure"     # azure | openai | deepseek | qwen

    # OpenAI 官方
    OPENAI_API_KEY: str = ""

    # Azure OpenAI - gpt-4o-2 部署
    AZURE_OPENAI_ENDPOINT_GPT4O2: str = ""  # https://leonchou-dalle3.cognitiveservices.azure.com
    AZURE_OPENAI_API_KEY_GPT4O2: str = ""
    AZURE_OPENAI_DEPLOYMENT_GPT4O2: str = "gpt-4o-2"
    
    # Azure OpenAI - gpt-5.1 部署
    AZURE_OPENAI_ENDPOINT_GPT51: str = ""  # https://lzhou-mi4i4wju-eastus2.cognitiveservices.azure.com
    AZURE_OPENAI_API_KEY_GPT51: str = ""
    AZURE_OPENAI_DEPLOYMENT_GPT51: str = "gpt-5.1-chat"
    
    # Azure OpenAI 通用配置
    AZURE_OPENAI_API_VERSION: str = "2025-01-01-preview"
    
    # 默认使用的 Azure 部署 (gpt4o2 | gpt51)
    AZURE_DEFAULT_DEPLOYMENT: str = "gpt4o2"
    
    # OCR 使用的 Azure 部署（需要支持 vision）
    # 可选值: gpt4o2 | gpt51 | auto (auto 会尝试 gpt4o2，如果失败则尝试 gpt51)
    AZURE_OCR_DEPLOYMENT: str = "gpt4o2"

    # 向后兼容的旧配置（如果设置了，会优先使用）
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""

    # Qwen / DashScope
    DASH_SCOPE_API_KEY: str = ""
    
    # 阿里云 OCR 配置
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_OCR_ENDPOINT: str = "cn-hangzhou.aliyuncs.com"  # 默认杭州区域，格式: cn-hangzhou.aliyuncs.com
    
    # 阿里云 API 市场 APPCODE（用于试卷切题等云市场服务）
    # 获取方式：https://market.aliyun.com -> 购买服务后在控制台查看
    ALIYUN_APPCODE: str = ""
    
    # OCR 提供者选择
    # 可选值: llm (使用 LLM vision) | aliyun (使用阿里云 OCR) | auto (优先阿里云，失败则回退 LLM)
    OCR_PROVIDER: str = "auto"

    class Config:
        env_file = str(ENV_FILE)  # 使用绝对路径
        extra = "ignore"

settings = Settings()
