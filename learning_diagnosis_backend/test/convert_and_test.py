#!/usr/bin/env python3
"""
图片格式转换并测试 OCR
自动将图片转换为标准 JPG 格式，提高阿里云 OCR 的兼容性
"""

import requests
import json
import base64
import sys
from pathlib import Path
from PIL import Image
import io

BASE_URL = "http://127.0.0.1:8000"


def convert_to_standard_jpg(image_path: str) -> bytes:
    """
    将任意格式图片转换为标准 JPG 格式
    
    Args:
        image_path: 原始图片路径
    
    Returns:
        JPG 格式的图片二进制数据
    """
    print(f"🔄 转换图片格式为标准 JPG...")
    
    # 打开图片
    img = Image.open(image_path)
    
    # 显示原始信息
    print(f"   原始格式: {img.format}")
    print(f"   原始尺寸: {img.size}")
    print(f"   原始模式: {img.mode}")
    
    # 如果是 RGBA 或 P 模式（带透明度），转换为 RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        print(f"   检测到透明通道，转换为 RGB...")
        # 创建白色背景
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        print(f"   转换模式: {img.mode} -> RGB")
        img = img.convert('RGB')
    
    # 压缩图片（如果太大）
    max_size = 2048
    if img.width > max_size or img.height > max_size:
        print(f"   图片较大，调整尺寸...")
        ratio = min(max_size / img.width, max_size / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"   新尺寸: {img.size}")
    
    # 保存为 JPG（高质量）
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    jpg_data = buffer.getvalue()
    
    print(f"✅ 转换完成，JPG 大小: {len(jpg_data) / 1024:.2f} KB")
    
    return jpg_data


def test_ocr_with_converted_image(image_path: str):
    """
    使用转换后的图片测试 OCR
    """
    print("\n" + "="*80)
    print("🔍 OCR 测试（自动格式转换）")
    print("="*80)
    
    path = Path(image_path)
    if not path.exists():
        print(f"❌ 图片不存在: {image_path}")
        sys.exit(1)
    
    print(f"📁 原始图片: {path.name}")
    print(f"📏 原始大小: {path.stat().st_size / 1024:.2f} KB")
    
    try:
        # 转换图片
        jpg_data = convert_to_standard_jpg(image_path)
        
        # Base64 编码
        image_base64 = base64.b64encode(jpg_data).decode('utf-8')
        print(f"📦 Base64 编码长度: {len(image_base64)} 字符")
        
        # 准备请求
        ocr_payload = {
            "image_url": None,
            "image_base64": image_base64
        }
        
        # 发送请求
        print(f"\n📤 发送 OCR 请求...")
        print(f"⏱️  超时时间: 120 秒")
        
        resp = requests.post(
            f"{BASE_URL}/api/v1/ocr/parse",
            json=ocr_payload,
            timeout=120
        )
        resp.raise_for_status()
        ocr_result = resp.json()
        
        print("\n✅ OCR 成功！")
        print(f"📊 识别到的题目数量: {len(ocr_result.get('problems', []))}")
        
        # 显示识别的原始文本
        if ocr_result.get("raw_text"):
            print("\n📝 识别的原始文本：")
            print("-"*80)
            print(ocr_result["raw_text"])
            print("-"*80)
        
        # 显示识别到的题目
        for i, problem in enumerate(ocr_result.get("problems", []), 1):
            print(f"\n📋 题目 {i}:")
            print(f"  类型: {problem.get('type', 'unknown')}")
            print(f"  难度: {problem.get('difficulty', 'unknown')}")
            print(f"  内容: {problem.get('question', '')[:150]}...")
            if problem.get('options'):
                print(f"  选项: {problem.get('options')}")
        
        return ocr_result
        
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时！")
        sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ OCR 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误响应: {e.response.text[:500]}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test/convert_and_test.py <图片路径>")
        print("示例: python test/convert_and_test.py ~/Downloads/image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # 检查是否安装了 Pillow
    try:
        import PIL
    except ImportError:
        print("❌ 缺少 Pillow 库，请安装：")
        print("   pip install Pillow")
        sys.exit(1)
    
    test_ocr_with_converted_image(image_path)


if __name__ == "__main__":
    main()

