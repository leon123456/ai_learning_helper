#!/usr/bin/env python3
"""
测试图片 URL 的可访问性
"""

import requests
import time

# 测试 URL
test_url = "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"

print("="*80)
print("🧪 测试图片 URL 可访问性")
print("="*80)
print(f"\n图片 URL: {test_url}\n")

# 测试 1: 直接访问
print("测试 1: 直接访问图片 URL")
try:
    resp = requests.get(test_url, timeout=10)
    print(f"  状态码: {resp.status_code}")
    print(f"  响应大小: {len(resp.content) / 1024:.2f} KB")
    print(f"  Content-Type: {resp.headers.get('Content-Type')}")
    if resp.status_code == 200:
        print("  ✅ URL 可访问")
    else:
        print("  ❌ URL 访问失败")
except Exception as e:
    print(f"  ❌ 异常: {e}")

# 测试 2: 从阿里云视角访问（通过 API）
print("\n测试 2: 通过阿里云 OCR API 访问")
print("  等待 3 秒后测试...")
time.sleep(3)

BASE_URL = "http://127.0.0.1:8000"
ocr_payload = {
    "image_url": test_url,
    "image_base64": None
}

try:
    resp = requests.post(
        f"{BASE_URL}/api/v1/ocr/parse",
        json=ocr_payload,
        timeout=30
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"  ✅ OCR 成功")
        print(f"  识别到 {len(result.get('problems', []))} 道题目")
    else:
        print(f"  ❌ OCR 失败: HTTP {resp.status_code}")
        try:
            error = resp.json()
            detail = error.get('detail', '')
            print(f"  错误: {detail[:200]}")
            
            # 分析错误类型
            if "unavailable" in detail or "timed out" in detail:
                print("\n  💡 分析: 阿里云无法访问该 URL")
                print("     可能原因:")
                print("     1. ImgBB 限制了阿里云服务器的访问")
                print("     2. 图床短时间内请求过多")
                print("     3. 网络波动")
            elif "415" in detail:
                print("\n  💡 分析: 图片格式问题")
            elif "401" in detail:
                print("\n  💡 分析: 权限问题")
        except:
            print(f"  错误响应: {resp.text[:200]}")
            
except Exception as e:
    print(f"  ❌ 异常: {e}")

# 建议
print("\n" + "="*80)
print("💡 建议")
print("="*80)
print("""
如果直接访问成功，但 OCR 失败：
  → 说明是阿里云访问图床的问题
  → 解决方案:
     1. 等待几分钟后重试
     2. 使用阿里云 OSS 存储图片
     3. 使用其他图床（如 SM.MS, Imgur）
     4. 本地部署文件服务器

如果都失败：
  → 图片 URL 本身有问题
  → 检查 URL 是否正确
""")

