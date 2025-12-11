#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷结构化识别测试脚本

测试阿里云 RecognizeEduPaperStructed API（精细版结构化切题）

使用方式：
1. 仅测试试卷识别：
   python test/test_paper_ocr.py

2. 测试试卷识别 + 批量诊断（需要提供答案）：
   python test/test_paper_ocr.py --with-diagnose

说明：
- 使用图片 URL 方式（更稳定）
- 自动切题、识别题干、选项、公式
- 返回题目坐标（可用于前端高亮）
- 支持整页、拍照、教辅、练习册
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.llm import LLMClient
from app.services.paper_diagnostic import PaperDiagnosticService
from app.schemas.paper import QuestionAnswer


# 测试用的试卷图片 URL（示例）
# 这里使用一个物理试卷的图片，包含多道题目
TEST_IMAGE_URL = "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"


async def test_paper_recognition():
    """测试试卷结构化识别"""
    print("\n" + "="*80)
    print("📄 测试试卷结构化识别")
    print("="*80)
    print(f"测试图片: {TEST_IMAGE_URL}")
    print()
    
    try:
        # 初始化 LLM 客户端
        llm = LLMClient()
        
        # 创建试卷诊断服务
        service = PaperDiagnosticService(llm)
        
        # 识别并解析试卷
        paper_structure, questions = await service.recognize_and_parse_paper(
            image_url=TEST_IMAGE_URL
        )
        
        # 打印识别结果
        print("\n" + "="*80)
        print("📊 识别结果汇总")
        print("="*80)
        print(f"✅ 试卷尺寸: {paper_structure.width} x {paper_structure.height}")
        print(f"✅ 识别到 {len(paper_structure.part_info)} 个大题分区")
        print(f"✅ 识别到 {len(questions)} 道题目")
        
        if paper_structure.figure:
            print(f"✅ 识别到 {len(paper_structure.figure)} 个图形元素")
        
        print("\n" + "-"*80)
        print("📋 题目详情")
        print("-"*80)
        
        for i, question in enumerate(questions, 1):
            print(f"\n【题目 {question.index}】（{question.section_title}）")
            print(f"  题型: {question.type}")
            print(f"  题干: {question.question}")
            
            if question.options:
                print(f"  选项:")
                for opt in question.options:
                    print(f"    {opt}")
            
            # 打印坐标信息（前端可用于高亮）
            if question.position and len(question.position) > 0:
                first_pos = question.position[0]
                if len(first_pos) >= 2:
                    print(f"  位置: ({first_pos[0].x}, {first_pos[0].y}) - ({first_pos[2].x}, {first_pos[2].y})")
        
        print("\n" + "="*80)
        print("✅ 试卷识别测试完成")
        print("="*80 + "\n")
        
        return paper_structure, questions
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def test_batch_diagnose(questions):
    """测试批量诊断"""
    print("\n" + "="*80)
    print("🔍 测试批量诊断")
    print("="*80)
    
    # 模拟用户答案（这里需要根据实际题目设置）
    # 示例：假设有3道选择题
    mock_answers = [
        QuestionAnswer(question_index=1, user_answer="A"),
        QuestionAnswer(question_index=2, user_answer="B"),
        QuestionAnswer(question_index=3, user_answer=""),  # 未作答
    ]
    
    # 只取前3道题进行测试（避免测试时间过长）
    test_questions = questions[:min(3, len(questions))]
    
    print(f"测试题目数: {len(test_questions)}")
    print(f"模拟答案数: {len(mock_answers)}")
    print()
    
    try:
        # 初始化 LLM 客户端
        llm = LLMClient()
        
        # 创建试卷诊断服务
        service = PaperDiagnosticService(llm)
        
        # 批量诊断
        result = await service.batch_diagnose(
            questions=test_questions,
            answers=mock_answers
        )
        
        # 打印诊断结果
        print("\n" + "="*80)
        print("📊 诊断结果汇总")
        print("="*80)
        
        summary = result.summary
        print(f"总题数: {summary.total_questions}")
        print(f"已作答: {summary.answered_questions}")
        print(f"正确: {summary.correct_count}")
        print(f"错误: {summary.wrong_count}")
        print(f"未作答: {summary.unanswered_count}")
        print(f"正确率: {summary.accuracy:.1f}%")
        print(f"平均掌握度: {summary.average_mastery:.1f}%")
        
        print("\n" + "-"*80)
        print("📈 按题型统计")
        print("-"*80)
        for q_type, stats in summary.stats_by_type.items():
            print(f"\n{q_type}:")
            print(f"  总数: {stats.total}")
            print(f"  正确: {stats.correct}")
            print(f"  错误: {stats.wrong}")
            print(f"  未作答: {stats.unanswered}")
            print(f"  正确率: {stats.accuracy:.1f}%")
        
        if summary.weak_knowledge_points:
            print("\n" + "-"*80)
            print("⚠️  薄弱知识点")
            print("-"*80)
            for weak_kp in summary.weak_knowledge_points:
                print(f"\n{weak_kp.knowledge}:")
                print(f"  错误次数: {weak_kp.error_count}/{weak_kp.total_count}")
                print(f"  正确率: {weak_kp.accuracy:.1f}%")
                print(f"  建议练习: {weak_kp.recommended_practice_count} 题")
        
        print("\n" + "-"*80)
        print("💡 总体建议")
        print("-"*80)
        print(summary.overall_suggestion)
        
        print("\n" + "-"*80)
        print("📝 每道题的详细诊断")
        print("-"*80)
        
        for item in result.results:
            print(f"\n【题目 {item.question_index}】")
            diagnose = item.diagnose_result
            
            status = "✅ 正确" if diagnose.correct else "❌ 错误"
            if diagnose.error_type == "未作答":
                status = "⚪ 未作答"
            
            print(f"  状态: {status}")
            print(f"  用户答案: {diagnose.user_answer}")
            print(f"  正确答案: {diagnose.correct_answer}")
            print(f"  错误类型: {diagnose.error_type}")
            print(f"  掌握度: {diagnose.mastery_score}%")
            print(f"  分析: {diagnose.analysis[:100]}..." if len(diagnose.analysis) > 100 else f"  分析: {diagnose.analysis}")
            print(f"  建议: {diagnose.next_action[:100]}..." if len(diagnose.next_action) > 100 else f"  建议: {diagnose.next_action}")
        
        print("\n" + "="*80)
        print("✅ 批量诊断测试完成")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试试卷结构化识别")
    parser.add_argument(
        "--with-diagnose",
        action="store_true",
        help="同时测试批量诊断功能（需要较长时间）"
    )
    parser.add_argument(
        "--image-url",
        type=str,
        default=TEST_IMAGE_URL,
        help="自定义测试图片 URL"
    )
    
    args = parser.parse_args()
    
    # 如果提供了自定义图片 URL，更新全局变量
    global TEST_IMAGE_URL
    if args.image_url:
        TEST_IMAGE_URL = args.image_url
    
    # 测试试卷识别
    paper_structure, questions = await test_paper_recognition()
    
    if not questions:
        print("❌ 试卷识别失败，跳过批量诊断测试")
        return
    
    # 如果指定了 --with-diagnose，则继续测试批量诊断
    if args.with_diagnose:
        await test_batch_diagnose(questions)
    else:
        print("\n💡 提示: 使用 --with-diagnose 参数可以同时测试批量诊断功能")


if __name__ == "__main__":
    asyncio.run(main())

