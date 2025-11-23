#!/usr/bin/env python3
"""
测试：使用图片 URL 调用阿里云 OCR（验证权限和 API 是否正常）
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 使用在线图片 URL 测试（避免 base64 body 的问题）
test_cases = [
    {
        "name": "在线图片 URL",
        "payload": {
            "image_url": "https://img.alicdn.com/imgextra/i1/O1CN01WfZHah1yGw8K8F3Lq_!!6000000006551-2-tps-600-400.png",
            "image_base64": None
        }
    },
    {
        "name": "用户的图片 URL",
        "payload": {
            "image_url": "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png",
            "image_base64": None
        }
    }
]

print("="*80)
print("🧪 测试阿里云 OCR - 使用图片 URL")
print("="*80)
print("\n目的：验证权限已配置，且 URL 方式是否能正常工作\n")

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"测试 {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"图片 URL: {test['payload']['image_url']}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/ocr/parse",
            json=test['payload'],
            timeout=120
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print("\n✅ 成功！")
            print(f"识别到 {len(result.get('problems', []))} 道题目")
            if result.get('raw_text'):
                print(f"\n原始文本（前200字）：\n{result['raw_text'][:200]}...")
        else:
            print(f"\n❌ 失败！HTTP {resp.status_code}")
            try:
                error = resp.json()
                print(f"错误详情: {json.dumps(error, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误响应: {resp.text[:500]}")
                
    except Exception as e:
        print(f"\n❌ 异常: {e}")

print("\n" + "="*80)
print("💡 结论")
print("="*80)
print("""
如果 URL 方式成功：
  → body 参数处理有问题，需要修复 base64 → body 的转换
  
如果 URL 方式也失败（415）：
  → 阿里云 OCR 服务配置或网络问题
  
如果权限错误（401）：
  → RAM 权限配置未生效，需要等待或重新配置
""")

