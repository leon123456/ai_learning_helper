#!/usr/bin/env python3
"""
测试脚本 - 支持本地图片上传
使用方法：
    python test/test_with_local_image.py                    # 使用默认 URL 图片
    python test/test_with_local_image.py /path/to/image.jpg  # 使用本地图片
"""

import requests
import json
import base64
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def image_to_base64(image_path: str) -> str:
    """
    将本地图片转换为 base64 编码
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        base64 编码的字符串（不含前缀）
    """
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')


def test_ocr(image_path: str = None, image_url: str = None):
    """
    测试 OCR 功能
    
    Args:
        image_path: 本地图片路径（优先）
        image_url: 图片 URL（备选）
    """
    print("\n" + "="*80)
    print("🔍 OCR 测试")
    print("="*80)
    
    # 准备请求数据
    ocr_payload = {
        "image_url": None,
        "image_base64": None
    }
    
    if image_path:
        # 使用本地图片
        path = Path(image_path)
        if not path.exists():
            print(f"❌ 图片不存在: {image_path}")
            sys.exit(1)
        
        print(f"📁 加载本地图片: {path.name}")
        print(f"📏 文件大小: {path.stat().st_size / 1024:.2f} KB")
        
        try:
            ocr_payload["image_base64"] = image_to_base64(image_path)
            print(f"✅ Base64 编码完成，长度: {len(ocr_payload['image_base64'])} 字符")
        except Exception as e:
            print(f"❌ 读取图片失败: {e}")
            sys.exit(1)
    
    elif image_url:
        # 使用图片 URL
        print(f"🌐 使用图片 URL: {image_url}")
        ocr_payload["image_url"] = image_url
    
    else:
        print("❌ 请提供图片路径或 URL")
        sys.exit(1)
    
    # 发送 OCR 请求
    print(f"\n📤 发送 OCR 请求...")
    print(f"⏱️  超时时间: 120 秒")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/ocr/parse",
            json=ocr_payload,
            timeout=120  # 增加到 120 秒
        )
        resp.raise_for_status()
        ocr_result = resp.json()
        
        print("\n✅ OCR 成功！")
        print(f"📊 识别到的题目数量: {len(ocr_result.get('problems', []))}")
        
        # 显示识别的原始文本
        if ocr_result.get("raw_text"):
            print("\n📝 识别的原始文本：")
            print("-"*80)
            print(ocr_result["raw_text"][:500])  # 只显示前 500 字符
            if len(ocr_result["raw_text"]) > 500:
                print("... (已截断)")
            print("-"*80)
        
        if not ocr_result.get("problems"):
            print("⚠️  未识别到题目，请检查图片或重试")
            return None
        
        # 显示识别到的题目
        for i, problem in enumerate(ocr_result["problems"], 1):
            print(f"\n📋 题目 {i}:")
            print(f"  类型: {problem.get('type', 'unknown')}")
            print(f"  难度: {problem.get('difficulty', 'unknown')}")
            print(f"  内容: {problem.get('question', '')[:100]}...")
            if problem.get('options'):
                print(f"  选项数量: {len(problem['options'])}")
        
        return ocr_result
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时！请检查：")
        print("   1. 图片文件是否太大（建议 < 5MB）")
        print("   2. 网络连接是否正常")
        print("   3. 服务器是否响应")
        sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ OCR 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误响应: {e.response.text[:500]}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ OCR 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_diagnose(ocr_result: dict, user_answer: str = ""):
    """
    测试诊断功能
    
    Args:
        ocr_result: OCR 识别结果
        user_answer: 用户答案
    """
    print("\n" + "="*80)
    print("🧠 诊断测试")
    print("="*80)
    
    if not ocr_result or not ocr_result.get("problems"):
        print("❌ 没有可诊断的题目")
        return
    
    # 获取第一道题
    parsed_problem = ocr_result["problems"][0]
    
    # 转换为 Problem 格式（添加 correct_answer 字段）
    problem = {
        "type": parsed_problem.get("type", "short_answer"),
        "question": parsed_problem.get("question", ""),
        "options": parsed_problem.get("options"),
        "knowledge_points": parsed_problem.get("knowledge_points", []),
        "difficulty": parsed_problem.get("difficulty", "medium"),
        "correct_answer": parsed_problem.get("correct_answer", None)
    }
    
    # 如果没有提供用户答案，使用默认值
    if not user_answer:
        user_answer = "我不会"  # 默认答案
    
    diagnose_payload = {
        "problem": problem,
        "user_answer": user_answer
    }
    
    print(f"📝 用户答案: {user_answer}")
    print(f"⏱️  超时时间: 90 秒")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/diagnose",
            json=diagnose_payload,
            timeout=90  # 增加到 90 秒
        )
        resp.raise_for_status()
        result = resp.json()
        
        print("\n✅ 诊断成功！")
        print("\n🎯 诊断结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except requests.exceptions.Timeout:
        print("❌ 诊断请求超时！")
        sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 诊断请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误响应: {e.response.text[:500]}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ 诊断处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    # 默认测试图片 URL
    default_image_url = "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 使用本地图片
        image_path = sys.argv[1]
        ocr_result = test_ocr(image_path=image_path)
    else:
        # 使用默认 URL
        print("💡 提示: 可以使用本地图片测试")
        print(f"   用法: python {sys.argv[0]} /path/to/image.jpg\n")
        ocr_result = test_ocr(image_url=default_image_url)
    
    # 如果 OCR 成功，继续测试诊断
    if ocr_result:
        # 可以通过命令行传入用户答案（可选）
        user_answer = sys.argv[2] if len(sys.argv) > 2 else ""
        test_diagnose(ocr_result, user_answer)


if __name__ == "__main__":
    main()

