#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 PaperCut 解析逻辑

使用已保存的测试结果验证解析函数的正确性
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_parse_paper_cut():
    """测试解析 PaperCut 响应"""
    from app.services.aliyun_paper_cut import (
        parse_paper_cut_response,
        convert_to_parsed_questions,
        extract_question_and_options,
    )
    
    print("=" * 80)
    print("📋 测试 PaperCut 解析逻辑")
    print("=" * 80)
    
    # 加载测试数据
    result_file = Path(__file__).parent / "test_results" / "paper_cut_sdk_20251210_210805.json"
    
    if not result_file.exists():
        print(f"❌ 测试数据文件不存在: {result_file}")
        return
    
    with open(result_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    response_data = test_data["response"]
    
    # 测试 1: 解析完整响应
    print("\n📊 测试 1: parse_paper_cut_response")
    print("-" * 40)
    
    parsed = parse_paper_cut_response(response_data)
    
    print(f"页面数量: {parsed['page_count']}")
    print(f"题目总数: {parsed['total_questions']}")
    
    for page in parsed["pages"]:
        print(f"\n页面 {page['page_id']} ({page['width']}x{page['height']}):")
        for q in page["questions"]:
            opt_info = f" ({len(q['options'])}选项)" if q['options'] else ""
            formula_info = " 📐公式" if q['has_formula'] else ""
            print(f"  [{q['index']}] {q['type']}{opt_info}{formula_info}")
            print(f"      题干: {q['question'][:60]}...")
            if q['options']:
                print(f"      选项: {q['options']}")
    
    # 测试 2: 转换为 ParsedQuestion 格式
    print("\n\n📊 测试 2: convert_to_parsed_questions")
    print("-" * 40)
    
    questions = convert_to_parsed_questions(response_data)
    
    print(f"转换后题目数: {len(questions)}")
    
    for q in questions:
        print(f"\n题目 {q['index']}:")
        print(f"  类型: {q['type']}")
        print(f"  题干: {q['question'][:80]}...")
        if q['options']:
            print(f"  选项数: {len(q['options'])}")
        print(f"  包含公式: {q['has_formula']}")
        print(f"  原始文本长度: {len(q['raw_text'])} 字符")
    
    # 测试 3: 单独测试选项提取
    print("\n\n📊 测试 3: extract_question_and_options")
    print("-" * 40)
    
    test_cases = [
        "1.(1+5i)i的虚部为 A.-1 B.0 C.1 D.6",
        "2.设全集U={1，2，3，4}，则$$C_U A$$中元素个数为 A.0 B.3 C.5 D.8",
        "3.若x>0，求f(x)的最小值",
        "4.证明：三角形内角和为180度",
        "5.填空题：2+2=____",
    ]
    
    for text in test_cases:
        question, options, qtype = extract_question_and_options(text)
        print(f"\n输入: {text[:50]}...")
        print(f"  类型: {qtype}")
        print(f"  题干: {question[:40]}..." if len(question) > 40 else f"  题干: {question}")
        print(f"  选项: {options if options else '无'}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_parse_paper_cut()
