#!/usr/bin/env python3
"""
调试阿里云 OCR body 参数
测试不同的 body 参数格式
"""

import asyncio
import base64
import sys
from pathlib import Path

# 设置环境变量（模拟 .env）
import os
os.environ['ALIYUN_ACCESS_KEY_ID'] = input("请输入 ALIYUN_ACCESS_KEY_ID: ").strip()
os.environ['ALIYUN_ACCESS_KEY_SECRET'] = input("请输入 ALIYUN_ACCESS_KEY_SECRET: ").strip()
os.environ['ALIYUN_OCR_ENDPOINT'] = 'cn-hangzhou.aliyuncs.com'

from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models


async def test_body_format(image_path: str):
    """测试不同的 body 参数格式"""
    
    print("="*80)
    print("🧪 测试阿里云 OCR body 参数格式")
    print("="*80)
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    print(f"\n📁 图片信息:")
    print(f"  路径: {image_path}")
    print(f"  大小: {len(image_bytes) / 1024:.2f} KB")
    print(f"  前10字节: {image_bytes[:10].hex()}")
    
    # 创建客户端
    config = open_api_models.Config(
        access_key_id=os.environ['ALIYUN_ACCESS_KEY_ID'],
        access_key_secret=os.environ['ALIYUN_ACCESS_KEY_SECRET'],
    )
    config.endpoint = f'ocr-api.{os.environ["ALIYUN_OCR_ENDPOINT"]}'
    client = OcrApi20210707Client(config)
    
    # 测试方案
    test_cases = [
        {
            "name": "方案 1: body = 原始二进制（推荐）",
            "body": image_bytes,
            "desc": "直接传入图片的二进制数据"
        },
        {
            "name": "方案 2: body = base64 字符串",
            "body": base64.b64encode(image_bytes).decode('utf-8'),
            "desc": "传入 base64 编码的字符串"
        },
        {
            "name": "方案 3: body = base64 字节",
            "body": base64.b64encode(image_bytes),
            "desc": "传入 base64 编码的字节"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"说明: {test['desc']}")
        print(f"类型: {type(test['body'])}")
        print(f"长度: {len(test['body']) if hasattr(test['body'], '__len__') else 'N/A'}")
        
        request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
        request.body = test['body']
        
        runtime = util_models.RuntimeOptions(
            read_timeout=30000,
            connect_timeout=10000,
        )
        
        try:
            response = await client.recognize_edu_question_ocr_with_options_async(request, runtime)
            
            if response and response.body:
                print("\n✅ 成功！")
                print(f"状态码: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
                
                if hasattr(response.body, 'data') and response.body.data:
                    import json
                    data = json.loads(response.body.data)
                    content = data.get('content', '')
                    print(f"识别内容（前100字）: {content[:100]}...")
                else:
                    print("响应体: ", response.body)
                
                print(f"\n🎉 {test['name']} 成功！这是正确的方式！")
                return test['name']
            else:
                print("\n⚠️  响应为空")
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ 失败: {error_msg[:200]}")
            
            # 分析错误
            if "415" in error_msg or "format" in error_msg.lower():
                print("   → 格式不支持，尝试下一个方案...")
            elif "401" in error_msg or "authorized" in error_msg.lower():
                print("   → 权限错误！请检查 AccessKey 配置")
                return None
            elif "400" in error_msg:
                print("   → 参数错误")
            else:
                print(f"   → 其他错误: {error_msg}")
    
    print("\n" + "="*80)
    print("❌ 所有方案都失败了")
    print("="*80)
    return None


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test/debug_body.py <图片路径>")
        print("示例: python test/debug_body.py ~/Downloads/test.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        sys.exit(1)
    
    result = await test_body_format(image_path)
    
    if result:
        print(f"\n✅ 结论: {result}")
    else:
        print("\n💡 建议:")
        print("  1. 检查 AccessKey 权限是否正确")
        print("  2. 尝试使用图片 URL 方式")
        print("  3. 联系阿里云技术支持")


if __name__ == "__main__":
    asyncio.run(main())

