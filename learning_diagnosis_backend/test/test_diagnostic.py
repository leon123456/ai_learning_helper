import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*80)
print("🧪 学习诊断系统测试")
print("="*80)

# =============== 1. OCR 识别图片 ===============

# 使用图片 URL（推荐：阿里云 OCR URL 方式稳定可靠）
# 注意：如果使用 ImgBB 等免费图床，短时间内频繁请求可能被限制
# 建议：使用阿里云 OSS 或其他稳定图床
ocr_payload = {
    # 选项 1: ImgBB（可能有频率限制）
    "image_url": "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png",
    
    # 选项 2: 如果上面失败，可以换成其他图床或本地服务器
    # "image_url": "http://localhost:8001/test_image.png",
    
    "image_base64": None
}

print("\n📸 步骤 1: OCR 识别图片")
print(f"图片 URL: {ocr_payload['image_url']}")
print("正在识别...")

try:
    resp = requests.post(f"{BASE_URL}/api/v1/ocr/parse", json=ocr_payload, timeout=120)
    resp.raise_for_status()
    ocr_result = resp.json()
    
    print("\n✅ OCR 识别成功！")
    print(f"识别到的题目数量: {len(ocr_result.get('problems', []))}")
    
    # 显示识别的原始文本（可选）
    if ocr_result.get("raw_text"):
        print(f"\n📝 识别的原始文本（前 200 字）：")
        print("-"*80)
        print(ocr_result["raw_text"][:200] + "...")
        print("-"*80)
    
    if not ocr_result.get("problems"):
        print("\n❌ 未识别到题目，请检查图片内容")
        exit(1)
    
    # 显示第一道题的详细信息
    parsed_problem = ocr_result["problems"][0]
    print(f"\n📋 题目详情：")
    print(f"  题目类型: {parsed_problem.get('type', 'unknown')}")
    print(f"  难度等级: {parsed_problem.get('difficulty', 'unknown')}")
    print(f"  知识点: {', '.join(parsed_problem.get('knowledge_points', []))}")
    print(f"  题目内容: {parsed_problem.get('question', '')[:150]}...")
    
    if parsed_problem.get('options'):
        print(f"  选项:")
        options = parsed_problem.get('options', [])
        if isinstance(options, list):
            # options 是列表格式：["A. xxx", "B. xxx", ...]
            for opt in options:
                print(f"    {opt}")
        elif isinstance(options, dict):
            # options 是字典格式：{"A": "xxx", "B": "xxx", ...}
            for opt_key, opt_val in options.items():
                print(f"    {opt_key}: {opt_val}")
    
except requests.exceptions.Timeout:
    print("\n❌ 请求超时！可能原因：")
    print("  - 图片过大或网络较慢")
    print("  - 服务器响应时间过长")
    exit(1)
except requests.exceptions.RequestException as e:
    print(f"\n❌ OCR 请求失败: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_detail = e.response.json()
            print("\n错误详情:")
            print(json.dumps(error_detail, ensure_ascii=False, indent=2))
        except:
            print(f"\n错误响应: {e.response.text[:500]}")
    exit(1)
except Exception as e:
    print(f"\n❌ OCR 处理失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)


# =============== 2. 学习诊断 ===============

print("\n" + "="*80)
print("🧠 步骤 2: 学习诊断")
print("="*80)

# 将 ParsedProblem 转换为 Problem（添加 correct_answer 字段）
problem = {
    "type": parsed_problem.get("type", "short_answer"),
    "question": parsed_problem.get("question", ""),
    "options": parsed_problem.get("options"),
    "knowledge_points": parsed_problem.get("knowledge_points", []),
    "difficulty": parsed_problem.get("difficulty", "medium"),
    "correct_answer": parsed_problem.get("correct_answer", None)
}

# 用户答案（可以修改为不同的测试答案）
user_answer = "1.1×10⁸"  # 示例答案
print(f"\n👤 用户答案: {user_answer}")

diagnose_payload = {
    "problem": problem,
    "user_answer": user_answer
}

print("正在诊断...")

try:
    resp = requests.post(f"{BASE_URL}/api/v1/diagnose", json=diagnose_payload, timeout=90)
    resp.raise_for_status()
    result = resp.json()
    
    print("\n✅ 诊断完成！")
    print("\n" + "="*80)
    print("📊 诊断结果")
    print("="*80)
    
    # 格式化显示诊断结果
    print(f"\n✓ 答案正确性: {'✅ 正确' if result.get('correct') else '❌ 错误'}")
    print(f"✓ 错误类型: {result.get('error_type', 'N/A')}")
    print(f"✓ 掌握程度: {result.get('mastery_score', 0)}/100")
    
    if result.get('analysis'):
        print(f"\n📖 分析:")
        print(f"  {result['analysis']}")
    
    if result.get('next_action'):
        print(f"\n💡 建议:")
        print(f"  {result['next_action']}")
    
    if result.get('knowledge_gap'):
        print(f"\n🎯 知识点诊断:")
        for gap in result['knowledge_gap']:
            print(f"  - {gap}")
    
    # 显示完整的 JSON 结果（可选）
    print(f"\n📄 完整结果（JSON）:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except requests.exceptions.Timeout:
    print("\n❌ 诊断请求超时！")
    exit(1)
except requests.exceptions.RequestException as e:
    print(f"\n❌ 诊断请求失败: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_detail = e.response.json()
            print("\n错误详情:")
            print(json.dumps(error_detail, ensure_ascii=False, indent=2))
        except:
            print(f"\n错误响应: {e.response.text[:500]}")
    exit(1)
except Exception as e:
    print(f"\n❌ 诊断处理失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*80)
print("🎉 测试完成！")
print("="*80)
