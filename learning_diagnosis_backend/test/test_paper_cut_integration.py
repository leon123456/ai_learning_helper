#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 PaperCut 与诊断服务的集成

验证：
1. PaperCut API 调用成功
2. 解析结果正确
3. 可以接入现有的诊断流程
"""

import asyncio
import base64
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(env_path)


async def test_paper_cut_integration():
    """测试 PaperCut 与诊断服务的集成"""
    from app.services.paper_diagnostic import PaperDiagnosticService
    from app.core.config import settings
    
    print("=" * 80)
    print("🧪 PaperCut 集成测试")
    print("=" * 80)
    
    # 检查配置
    if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
        print("❌ 未配置阿里云 AccessKey")
        return
    
    print(f"✅ 阿里云配置已加载 (AccessKey ID: {settings.ALIYUN_ACCESS_KEY_ID[:8]}...)")
    
    # 读取测试图片
    test_image = Path(__file__).parent / "test_png" / "2025gaokao1.png"
    
    if not test_image.exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    print(f"📄 测试图片: {test_image.name}")
    
    with open(test_image, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    print(f"   大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
    
    # 创建诊断服务（不需要 LLM，只测试 OCR 部分）
    class MockLLM:
        pass
    
    service = PaperDiagnosticService(MockLLM())
    
    # 测试 PaperCut 方法
    print("\n" + "-" * 40)
    print("📋 测试 recognize_and_parse_paper_cut")
    print("-" * 40)
    
    try:
        raw_data, questions = await service.recognize_and_parse_paper_cut(
            image_base64=image_base64,
            cut_type="question",
            image_type="scan",
            subject="Math",
        )
        
        print(f"\n✅ 识别成功！")
        print(f"   题目数量: {len(questions)}")
        
        print("\n📝 题目详情:")
        for q in questions:
            print(f"\n   题目 {q.index}:")
            print(f"      类型: {q.type}")
            print(f"      题干: {q.question[:60]}..." if len(q.question) > 60 else f"      题干: {q.question}")
            if q.options:
                print(f"      选项数: {len(q.options)}")
                for i, opt in enumerate(q.options[:2]):  # 只显示前2个选项
                    print(f"         {opt[:40]}..." if len(opt) > 40 else f"         {opt}")
                if len(q.options) > 2:
                    print(f"         ... 还有 {len(q.options) - 2} 个选项")
        
        # 保存结果
        result_dir = Path(__file__).parent / "test_results"
        result_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = result_dir / f"paper_cut_integration_{timestamp}.json"
        
        # 将 questions 转换为可序列化的格式
        questions_data = []
        for q in questions:
            questions_data.append({
                "index": q.index,
                "type": q.type,
                "question": q.question,
                "options": q.options,
                "has_figure": q.has_figure,
            })
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "test_time": datetime.now().isoformat(),
                "image": test_image.name,
                "api": "PaperCut",
                "question_count": len(questions),
                "questions": questions_data,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存: {result_file}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 集成测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_paper_cut_integration())
