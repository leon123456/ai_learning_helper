#!/usr/bin/env python3
"""
测试阿里云 OCR SDK 的正确用法
"""

import sys
import base64
from pathlib import Path

# 尝试导入阿里云 SDK
try:
    from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
    from alibabacloud_tea_util import models as util_models
except ImportError as e:
    print(f"❌ 缺少阿里云 SDK: {e}")
    print("请安装: pip install alibabacloud-ocr-api20210707")
    sys.exit(1)

def test_request_attributes():
    """测试 RecognizeEduQuestionOcrRequest 支持的属性"""
    print("="*80)
    print("🔍 检查 RecognizeEduQuestionOcrRequest 的属性")
    print("="*80)
    
    request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
    
    # 列出所有非私有属性
    attrs = [attr for attr in dir(request) if not attr.startswith('_')]
    
    print("\n支持的属性:")
    for attr in sorted(attrs):
        print(f"  ✓ {attr}")
    
    # 测试常见属性
    print("\n="*80)
    print("🧪 测试常见属性")
    print("="*80)
    
    test_attrs = ['url', 'body', 'img', 'prob', 'rotate']
    for attr in test_attrs:
        if hasattr(request, attr):
            print(f"  ✅ {attr:15} - 存在")
            try:
                # 尝试设置值
                if attr == 'url':
                    setattr(request, attr, "http://example.com/test.jpg")
                elif attr == 'body':
                    setattr(request, attr, b"test_bytes")
                elif attr == 'img':
                    setattr(request, attr, "test_base64")
                elif attr in ['prob', 'rotate']:
                    setattr(request, attr, True)
                print(f"                   类型: {type(getattr(request, attr))}")
            except Exception as e:
                print(f"                   设置失败: {e}")
        else:
            print(f"  ❌ {attr:15} - 不存在")
    
    print("\n" + "="*80)
    print("📖 根据官方文档:")
    print("="*80)
    print("""
  参数说明:
  - url:    图像 URL 地址（与 body 只能存在一个）
  - body:   图像二进制数据（与 url 只能存在一个）
  
  注意: 
  1. 官方文档中提到的 'img' 字段在 SDK 中对应 'body'
  2. body 字段接受的是图片的二进制数据
  3. 如果是 base64 字符串，需要先解码为二进制
    """)

def test_with_image(image_path: str):
    """使用真实图片测试"""
    print("\n" + "="*80)
    print("🖼️  真实图片测试")
    print("="*80)
    
    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        return
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    print(f"✅ 图片大小: {len(image_data) / 1024:.2f} KB")
    
    # 测试两种方式
    print("\n方式 1: body = 二进制数据")
    request1 = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
    request1.body = image_data
    print(f"  ✓ request.body 类型: {type(request1.body)}")
    print(f"  ✓ request.body 大小: {len(request1.body) if request1.body else 0} bytes")
    
    print("\n方式 2: body = base64 解码后的二进制")
    base64_str = base64.b64encode(image_data).decode('utf-8')
    print(f"  ✓ Base64 长度: {len(base64_str)} 字符")
    request2 = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
    # 阿里云 SDK 可能期望直接的二进制数据
    request2.body = image_data  # 直接使用二进制
    print(f"  ✓ request.body 类型: {type(request2.body)}")
    
    print("\n💡 建议:")
    print("  - body 字段应该直接传入图片的二进制数据（bytes）")
    print("  - 不需要 base64 编码，SDK 内部会处理")

if __name__ == "__main__":
    test_request_attributes()
    
    if len(sys.argv) > 1:
        test_with_image(sys.argv[1])
    else:
        print("\n💡 提示: 可以传入图片路径进行更多测试")
        print(f"   用法: python {sys.argv[0]} /path/to/image.jpg")

