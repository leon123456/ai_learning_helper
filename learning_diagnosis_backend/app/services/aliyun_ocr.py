# app/services/aliyun_ocr.py

"""
阿里云题目识别 OCR 服务
参考文档: https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeeduquestionocr
基于官方示例: app/demo/alibabacloud_sample/sample.py
"""

import json
from typing import Optional
from app.core.config import settings


class AliyunOCRClient:
    """阿里云 OCR 客户端"""
    
    def __init__(self):
        """
        初始化阿里云 OCR 客户端
        
        凭据配置优先级：
        1. .env 中的 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET（直接配置）
        2. 环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET
        3. 配置文件 ~/.alibabacloud/credentials
        """
        self.endpoint = settings.ALIYUN_OCR_ENDPOINT
        self.use_credential_client = False
        
        # 优先使用 .env 中的配置（更可靠）
        self.access_key_id = settings.ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = settings.ALIYUN_ACCESS_KEY_SECRET
        
        if self.access_key_id and self.access_key_secret:
            # 使用直接配置
            print(f"✅ 使用 .env 中配置的阿里云 AccessKey（ID: {self.access_key_id[:8]}...）")
        else:
            # 尝试使用 CredentialClient（从环境变量或配置文件读取）
            try:
                from alibabacloud_credentials.client import Client as CredentialClient
                self.credential_client = CredentialClient()
                self.use_credential_client = True
                print("✅ 使用阿里云 CredentialClient（从环境变量或配置文件读取）")
            except Exception as e:
                raise ValueError(
                    "阿里云 OCR 配置不完整。请选择以下方式之一：\n"
                    "【推荐】在 .env 文件中设置：\n"
                    "  ALIYUN_ACCESS_KEY_ID=你的AccessKeyId\n"
                    "  ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret\n"
                    "\n"
                    "或设置环境变量：\n"
                    "  export ALIBABA_CLOUD_ACCESS_KEY_ID='你的AccessKeyId'\n"
                    "  export ALIBABA_CLOUD_ACCESS_KEY_SECRET='你的AccessKeySecret'\n"
                    "\n"
                    "或创建配置文件 ~/.alibabacloud/credentials：\n"
                    "  [default]\n"
                    "  type = access_key\n"
                    "  access_key_id = 你的AccessKeyId\n"
                    "  access_key_secret = 你的AccessKeySecret\n"
                    f"\n原始错误: {e}"
                )
    
    async def recognize_question(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> str:
        """
        识别题目内容
        
        Args:
            image_url: 图片 URL
            image_base64: 图片 base64 编码（不含前缀）
        
        Returns:
            识别出的文本内容
        """
        from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
        from alibabacloud_tea_util import models as util_models
        from alibabacloud_tea_util.client import Client as UtilClient
        
        # 创建客户端配置
        if self.use_credential_client:
            # 使用 CredentialClient（推荐方式，从环境变量或配置文件读取）
            from alibabacloud_credentials.client import Client as CredentialClient
            credential = CredentialClient()
            config = open_api_models.Config(
                credential=credential
            )
        else:
            # 使用直接配置的 AccessKey（兼容方式）
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
            )
        
        # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
        # 如果 endpoint 已经包含 ocr-api. 前缀，则直接使用；否则添加前缀
        if self.endpoint.startswith('ocr-api.'):
            config.endpoint = self.endpoint
        else:
            config.endpoint = f'ocr-api.{self.endpoint}'
        client = OcrApi20210707Client(config)
        
        # 准备请求参数
        request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
        
        if image_url:
            # 使用图片 URL
            request.url = image_url
            print(f"  ✓ 使用 URL 方式: {image_url[:80]}...")
        elif image_base64:
            # 使用 base64 编码的图片
            # 如果包含前缀，去掉
            if image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",")[1]
            
            # 关键：body 字段需要的是图片的原始二进制数据
            # 将 base64 字符串解码为二进制
            import base64 as b64
            image_bytes = b64.b64decode(image_base64)
            request.body = image_bytes
            
            print(f"  ✓ 使用 body 方式")
            print(f"    - Base64 长度: {len(image_base64)} 字符")
            print(f"    - 二进制大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
            print(f"    - body 类型: {type(request.body)}")
        else:
            raise ValueError("必须提供 image_url 或 image_base64")
        
        try:
            # 调用 API（异步）
            runtime = util_models.RuntimeOptions(
                read_timeout=120000,  # 读取超时 120 秒（单位：毫秒）
                connect_timeout=30000,  # 连接超时 30 秒
            )
            response = await client.recognize_edu_question_ocr_with_options_async(request, runtime)
            
            # 解析响应
            if not response or not response.body:
                raise Exception("阿里云 OCR API 返回空响应")
            
            # 解析返回的 JSON 字符串
            data_str = response.body.data
            if not data_str:
                raise Exception("阿里云 OCR API 返回的 data 为空")
            
            data = json.loads(data_str)
            
            # 提取文本内容
            content = data.get("content", "")
            
            if not content:
                raise Exception("识别结果中未找到文本内容")
            
            return content
            
        except ImportError as e:
            # 模块导入错误，给出明确的安装提示
            raise ImportError(
                f"阿里云 OCR SDK 未安装。请运行以下命令安装：\n"
                f"pip install alibabacloud-ocr-api20210707 alibabacloud-tea-openapi alibabacloud-tea-util alibabacloud-credentials\n"
                f"原始错误: {e}"
            )
        except Exception as e:
            error_msg = str(e)
            # 如果是阿里云 SDK 的异常，提取更详细的错误信息
            if hasattr(e, 'message'):
                error_msg = e.message
            if hasattr(e, 'data') and e.data:
                recommend = e.data.get("Recommend", "")
                if recommend:
                    error_msg += f" 诊断地址: {recommend}"
            
            raise Exception(f"阿里云 OCR 识别失败: {error_msg}")


async def recognize_with_aliyun(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> str:
    """
    使用阿里云 OCR 识别题目
    
    Args:
        image_url: 图片 URL
        image_base64: 图片 base64 编码
    
    Returns:
        识别出的文本内容
    """
    client = AliyunOCRClient()
    return await client.recognize_question(image_url=image_url, image_base64=image_base64)

