import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# =============== 1. 先 OCR/parse 一张图片（可选） ===============
# 如果你已经有 parsed problem，也可以跳过 OCR 直接用

# 这里演示用图片 URL（你可替换为自己的题目）
ocr_payload = {
    "image_url": "https://i.ibb.co/4nT7dx3t/Screen-Shot-2025-11-16-173004-542.png",
    "image_base64": None
}

print("🔍 正在解析图片...")
resp = requests.post(f"{BASE_URL}/api/v1/ocr/parse", json=ocr_payload)
print("OCR result:")
print(resp.json())

parsed = resp.json()

problem = parsed["problems"][0]   # 获取第一道题


# =============== 2. 提交诊断（diagnose） ===============

diagnose_payload = {
    "problem": problem,
    "user_answer": "6"   # 你可以手动改
}

print("\n🧠 正在进行诊断...")
resp = requests.post(f"{BASE_URL}/api/v1/diagnose", json=diagnose_payload)
result = resp.json()

print("\n🎉 诊断结果：")
print(json.dumps(result, ensure_ascii=False, indent=2))
