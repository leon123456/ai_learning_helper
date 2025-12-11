#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考试卷识别测试 - 简化版

专门用于测试 test_png 目录下的 2025 高考试卷图片

使用方式：
    python test/test_gaokao_paper.py
    
    或者从任意目录运行：
    python /path/to/test_gaokao_paper.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import base64

# 检查阿里云配置
from app.core.config import settings

def check_aliyun_config():
    """检查阿里云配置是否完整"""
    if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
        print("\n" + "="*80)
        print("❌ 阿里云 OCR 配置不完整！")
        print("="*80)
        print("\n请在 .env 文件中添加以下配置：\n")
        print("# 阿里云 OCR 配置")
        print("ALIYUN_ACCESS_KEY_ID=你的AccessKeyId")
        print("ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret")
        print("ALIYUN_OCR_ENDPOINT=cn-hangzhou.aliyuncs.com")
        print("\n获取 AccessKey: https://ram.console.aliyun.com/manage/ak")
        print("确保 RAM 权限: AliyunOCRFullAccess 或 AliyunOCRReadOnlyAccess")
        print("="*80 + "\n")
        return False
    
    print(f"✅ 阿里云配置已加载 (AccessKey ID: {settings.ALIYUN_ACCESS_KEY_ID[:8]}...)")
    return True


async def test_gaokao_paper():
    """测试高考试卷识别"""
    
    print("\n" + "="*80)
    print("📄 2025 高考试卷识别测试")
    print("="*80)
    
    # 检查配置
    if not check_aliyun_config():
        return
    
    # 测试图片路径
    test_dir = Path(__file__).parent / "test_png"
    images = sorted(test_dir.glob("*.png"))
    
    if not images:
        print("❌ 未找到测试图片")
        return
    
    print(f"\n发现 {len(images)} 张测试图片:")
    for img in images:
        print(f"  - {img.name}")
    
    # 测试每张图片
    all_results = []
    
    for i, image_path in enumerate(images, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(images)}] 测试: {image_path.name}")
        print("="*80)
        
        try:
            # 将图片转换为 base64
            print("📦 读取图片并转换为 base64...")
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")
            
            print(f"   图片大小: {len(image_base64)} 字符")
            
            # 调用识别服务（直接使用阿里云 OCR，不需要 LLM）
            print("🔍 调用阿里云试卷识别 API...")
            import time
            start_time = time.time()
            
            # 导入阿里云试卷 OCR 服务
            from app.services.aliyun_paper_ocr import (
                recognize_paper_structure, 
                parse_question_from_aliyun,
                merge_question_with_options,
            )
            from app.schemas.paper import ParsedQuestion
            
            # 调用阿里云 API
            raw_data = await recognize_paper_structure(image_base64=image_base64)
            
            # 构建 PaperStructure
            from app.schemas.paper import PaperStructure
            paper_structure = PaperStructure(
                page_id=raw_data.get("page_id", 0),
                page_title=raw_data.get("page_title", ""),
                width=raw_data.get("width", 0),
                height=raw_data.get("height", 0),
                part_info=[],
                figure=raw_data.get("figure", []),
                raw_data=raw_data
            )
            
            # 获取所有配图和页面高度
            all_figures = raw_data.get("figure", [])
            page_height = raw_data.get("height", 0)
            
            # 第一步：解析所有题目（关联配图）
            parsed_questions_raw = []
            for part in raw_data.get("part_info", []):
                section_title = part.get("part_title", "")
                for subject in part.get("subject_list", []):
                    # 传递配图列表，让解析函数自动关联
                    parsed = parse_question_from_aliyun(
                        subject, 
                        all_figures=all_figures,
                        page_height=page_height
                    )
                    parsed["section_title"] = section_title
                    parsed_questions_raw.append(parsed)
            
            # 第二步：合并被错误分割的题目和选项
            print("🔧 检查并合并分割的题目...")
            parsed_questions_merged = merge_question_with_options(parsed_questions_raw)
            
            # 第三步：转换为 ParsedQuestion 对象
            questions = []
            for parsed in parsed_questions_merged:
                question = ParsedQuestion(
                    index=parsed["index"],
                    type=parsed["type"],
                    question=parsed["question"],
                    options=parsed["options"],
                    position=parsed["position"],
                    section_title=parsed.get("section_title", ""),
                    elements=parsed.get("elements"),
                    figures=parsed.get("figures", []),
                    has_figure=parsed.get("has_figure", False),
                    figure_description=parsed.get("figure_description"),
                )
                questions.append(question)
            
            recognition_time = time.time() - start_time
            
            # 记录结果
            result = {
                "image_name": image_path.name,
                "status": "success",
                "recognition_time": recognition_time,
                "total_questions": len(questions),
                "paper_info": {
                    "page_id": paper_structure.page_id,
                    "width": paper_structure.width,
                    "height": paper_structure.height,
                    "sections": []
                },
                "questions": [],
                "figures": raw_data.get("figure", []),  # 保存图片/图形坐标信息
            }
            
            # 统计大题信息
            for section in paper_structure.part_info:
                result["paper_info"]["sections"].append({
                    "title": section.part_title,
                    "count": len(section.subject_list)
                })
            
            # 记录题目信息
            for q in questions:
                # 将 PaperFigure 对象转换为字典
                figures_dict = []
                for fig in q.figures:
                    if hasattr(fig, 'model_dump'):
                        figures_dict.append(fig.model_dump())
                    elif hasattr(fig, 'dict'):
                        figures_dict.append(fig.dict())
                    elif isinstance(fig, dict):
                        figures_dict.append(fig)
                    else:
                        figures_dict.append(str(fig))
                
                result["questions"].append({
                    "index": q.index,
                    "type": q.type,
                    "section_title": q.section_title,
                    "question": q.question,
                    "options": q.options,
                    "has_position": bool(q.position),
                    "has_figure": q.has_figure,
                    "figure_count": len(q.figures),
                    "figure_description": q.figure_description,
                    "figures": figures_dict,  # 保存完整的配图信息
                })
            
            all_results.append(result)
            
            # 打印结果
            print(f"\n✅ 识别成功!")
            print(f"  ⏱️  耗时: {recognition_time:.2f} 秒")
            print(f"  📏 图片尺寸: {paper_structure.width} x {paper_structure.height}")
            print(f"  📊 识别到 {len(questions)} 道题目")
            
            if paper_structure.part_info:
                print(f"\n  📋 大题分区:")
                for section in paper_structure.part_info:
                    print(f"     - {section.part_title}: {len(section.subject_list)} 道题")
            
            print(f"\n  📝 题目详情:")
            for j, q in enumerate(questions[:10], 1):  # 只显示前10题
                preview = q.question[:80] + "..." if len(q.question) > 80 else q.question
                options_info = f"（{len(q.options)} 个选项）" if q.options else ""
                figure_info = f" 🖼️{len(q.figures)}图" if q.has_figure else ""
                print(f"     {q.index}. [{q.type}] {preview} {options_info}{figure_info}")
            
            if len(questions) > 10:
                print(f"     ... 还有 {len(questions) - 10} 道题目")
            
            # 打印图片/图形信息
            figures = raw_data.get("figure", [])
            if figures:
                print(f"\n  🖼️  识别到 {len(figures)} 个图片/图形:")
                for fig in figures[:5]:  # 只显示前5个
                    fig_type = fig.get("type", "unknown")
                    x, y = fig.get("x", 0), fig.get("y", 0)
                    w, h = fig.get("w", 0), fig.get("h", 0)
                    print(f"     - 类型: {fig_type}, 位置: ({x}, {y}), 尺寸: {w}x{h}")
                if len(figures) > 5:
                    print(f"     ... 还有 {len(figures) - 5} 个图形")
            else:
                print(f"\n  🖼️  未识别到题目配图")
            
        except Exception as e:
            print(f"\n❌ 识别失败")
            print(f"  错误: {e}")
            
            import traceback
            traceback.print_exc()
            
            result = {
                "image_name": image_path.name,
                "status": "failed",
                "error": str(e),
            }
            all_results.append(result)
    
    # 生成汇总报告
    print(f"\n{'='*80}")
    print("📊 测试汇总")
    print("="*80)
    
    success_count = sum(1 for r in all_results if r["status"] == "success")
    total_questions = sum(r.get("total_questions", 0) for r in all_results)
    
    print(f"测试图片数: {len(all_results)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(all_results) - success_count}")
    print(f"识别题目总数: {total_questions}")
    
    # 保存结果到文件
    output_dir = Path(__file__).parent / "test_results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"gaokao_test_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "test_images": [img.name for img in images],
            "results": all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 测试结果已保存: {output_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_gaokao_paper())

