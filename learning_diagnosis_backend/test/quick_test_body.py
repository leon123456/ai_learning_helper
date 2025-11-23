#!/usr/bin/env python3
"""
快速测试：找出正确的 body 参数格式
"""

import asyncio
import base64
import sys
from pathlib import Path

# 简化版：直接使用环境变量
from app.core.config import settings
from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models


async def test_formats(image_path: str):
    """测试不同的 body 格式"""
    
    print("="*80)
    print("🧪 测试阿里云 OCR body 参数")
    print("="*80)
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    print(f"\n📁 图片: {Path(image_path).name}")
    print(f"📏 大小: {len(image_bytes) / 1024:.2f} KB")
    
    # 创建客户端
    config = open_api_models.Config(
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
    )
    config.endpoint = f'ocr-api.{settings.ALIYUN_OCR_ENDPOINT}'
    client = OcrApi20210707Client(config)
    runtime = util_models.RuntimeOptions(read_timeout=30000, connect_timeout=10000)
    
    # 测试方案
    tests = [
        ("原始二进制", image_bytes),
        ("base64 字符串", base64.b64encode(image_bytes).decode('utf-8')),
        ("base64 字节", base64.b64encode(image_bytes)),
    ]
    
    for name, body_value in tests:
        print(f"\n{'='*80}")
        print(f"测试: {name}")
        print(f"类型: {type(body_value).__name__}, 长度: {len(body_value)}")
        print(f"{'='*80}")
        
        request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
        request.body = body_value
        
        try:
            response = await client.recognize_edu_question_ocr_with_options_async(request, runtime)
            
            if response and response.body and response.body.data:
                import json
                data = json.loads(response.body.data)
                content = data.get('content', '')[:100]
                print(f"✅ 成功！识别内容: {content}...")
                print(f"\n🎉 正确方式: {name}")
                return name
            else:
                print("⚠️  响应为空")
                
        except Exception as e:
            error = str(e)
            if "415" in error:
                print(f"❌ 415 错误: 格式不支持")
            elif "401" in error:
                print(f"❌ 401 错误: 权限问题")
            else:
                print(f"❌ 失败: {error[:150]}")
    
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test/quick_test_body.py <图片路径>")
        sys.exit(1)
    
    result = asyncio.run(test_formats(sys.argv[1]))
    
    if result:
        print(f"\n✅ 结论: 使用 '{result}' 格式")
    else:
        print("\n❌ 所有格式都失败")

