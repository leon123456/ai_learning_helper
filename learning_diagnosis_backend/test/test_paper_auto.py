#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷识别自动化测试框架

功能：
1. 自动扫描 test_png 目录下的所有图片
2. 启动本地文件服务器（或上传到图床）
3. 调用试卷识别 API
4. 验证识别结果
5. 生成详细的测试报告
6. 可选：模拟答案并进行批量诊断测试

使用方式：
1. 基本测试（仅识别）：
   python test/test_paper_auto.py

2. 完整测试（识别 + 诊断）：
   python test/test_paper_auto.py --with-diagnose

3. 使用图床上传（需要配置图床 API）：
   python test/test_paper_auto.py --use-imgbb --imgbb-key YOUR_API_KEY

4. 生成 HTML 报告：
   python test/test_paper_auto.py --html-report

5. 指定测试目录：
   python test/test_paper_auto.py --test-dir test/test_png
"""

import sys
import os
import asyncio
import json
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import http.server
import socketserver
import threading
import requests

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.llm import LLMClient
from app.services.paper_diagnostic import PaperDiagnosticService
from app.schemas.paper import QuestionAnswer


# ==================== 配置 ====================

# 测试配置
TEST_CONFIG = {
    "test_dir": "test/test_png",  # 测试图片目录
    "local_server_port": 8001,     # 本地文件服务器端口
    "api_base": "http://localhost:8000/api/v1",  # API 地址
    "output_dir": "test/test_results",  # 测试结果输出目录
}

# 图床配置（可选）
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"


# ==================== 工具函数 ====================

class LocalFileServer:
    """本地文件服务器，用于提供图片访问"""
    
    def __init__(self, directory: str, port: int):
        self.directory = Path(directory).resolve()
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """启动文件服务器"""
        os.chdir(self.directory.parent)
        
        Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer(("", self.port), Handler)
        
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        print(f"✅ 本地文件服务器已启动: http://localhost:{self.port}")
        time.sleep(1)  # 等待服务器启动
        
    def stop(self):
        """停止文件服务器"""
        if self.server:
            self.server.shutdown()
            print("✅ 本地文件服务器已停止")
    
    def get_url(self, file_path: Path) -> str:
        """获取文件的访问 URL"""
        relative_path = file_path.relative_to(self.directory.parent)
        return f"http://localhost:{self.port}/{relative_path.as_posix()}"


def upload_to_imgbb(image_path: Path, api_key: str) -> Optional[str]:
    """
    上传图片到 ImgBB 图床
    
    Args:
        image_path: 图片路径
        api_key: ImgBB API Key
    
    Returns:
        图片 URL，失败返回 None
    """
    if not api_key:
        print("⚠️  未配置 ImgBB API Key，跳过图床上传")
        return None
    
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        response = requests.post(
            IMGBB_UPLOAD_URL,
            data={
                "key": api_key,
                "image": image_data,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                url = result["data"]["url"]
                print(f"  ✅ 上传到 ImgBB: {url}")
                return url
        
        print(f"  ❌ ImgBB 上传失败: {response.text}")
        return None
        
    except Exception as e:
        print(f"  ❌ ImgBB 上传异常: {e}")
        return None


def image_to_base64(image_path: Path) -> str:
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ==================== 测试类 ====================

class PaperRecognitionTest:
    """试卷识别测试"""
    
    def __init__(
        self,
        test_dir: str,
        use_imgbb: bool = False,
        imgbb_key: str = "",
        use_local_server: bool = True,
        use_base64: bool = False,
    ):
        self.test_dir = Path(test_dir)
        self.use_imgbb = use_imgbb
        self.imgbb_key = imgbb_key
        self.use_local_server = use_local_server
        self.use_base64 = use_base64
        
        self.results: List[Dict[str, Any]] = []
        self.local_server: Optional[LocalFileServer] = None
        
        # 确保测试目录存在
        if not self.test_dir.exists():
            raise ValueError(f"测试目录不存在: {self.test_dir}")
    
    def setup(self):
        """测试前准备"""
        # 启动本地文件服务器（如果需要）
        if self.use_local_server and not self.use_imgbb and not self.use_base64:
            self.local_server = LocalFileServer(
                directory=str(self.test_dir),
                port=TEST_CONFIG["local_server_port"]
            )
            self.local_server.start()
    
    def teardown(self):
        """测试后清理"""
        # 停止本地文件服务器
        if self.local_server:
            self.local_server.stop()
    
    def get_test_images(self) -> List[Path]:
        """获取所有测试图片"""
        images = list(self.test_dir.glob("*.png"))
        images.extend(self.test_dir.glob("*.jpg"))
        images.extend(self.test_dir.glob("*.jpeg"))
        return sorted(images)
    
    async def test_single_image(self, image_path: Path) -> Dict[str, Any]:
        """
        测试单张图片的识别
        
        Returns:
            测试结果字典
        """
        print(f"\n{'='*80}")
        print(f"📄 测试图片: {image_path.name}")
        print(f"{'='*80}")
        
        result = {
            "image_name": image_path.name,
            "image_path": str(image_path),
            "status": "pending",
            "error": None,
            "recognition_time": 0,
            "total_questions": 0,
            "questions": [],
        }
        
        start_time = time.time()
        
        try:
            # 获取图片 URL 或 base64
            image_url = None
            image_base64 = None
            
            if self.use_base64:
                print("  📦 使用 base64 方式")
                image_base64 = image_to_base64(image_path)
                result["method"] = "base64"
            elif self.use_imgbb:
                print("  ☁️  上传到 ImgBB...")
                image_url = upload_to_imgbb(image_path, self.imgbb_key)
                if not image_url:
                    raise Exception("图床上传失败")
                result["method"] = "imgbb"
                result["image_url"] = image_url
            else:
                # 使用本地文件服务器
                image_url = self.local_server.get_url(image_path)
                print(f"  🌐 本地 URL: {image_url}")
                result["method"] = "local_server"
                result["image_url"] = image_url
            
            # 调用识别服务
            llm = LLMClient()
            service = PaperDiagnosticService(llm)
            
            paper_structure, questions = await service.recognize_and_parse_paper(
                image_url=image_url,
                image_base64=image_base64,
            )
            
            recognition_time = time.time() - start_time
            
            # 记录结果
            result["status"] = "success"
            result["recognition_time"] = recognition_time
            result["total_questions"] = len(questions)
            result["questions"] = [
                {
                    "index": q.index,
                    "type": q.type,
                    "section_title": q.section_title,
                    "question_preview": q.question[:100] + "..." if len(q.question) > 100 else q.question,
                    "has_options": bool(q.options),
                    "option_count": len(q.options) if q.options else 0,
                }
                for q in questions
            ]
            result["paper_structure"] = {
                "width": paper_structure.width,
                "height": paper_structure.height,
                "page_id": paper_structure.page_id,
                "sections": [
                    {
                        "title": section.part_title,
                        "question_count": len(section.subject_list)
                    }
                    for section in paper_structure.part_info
                ]
            }
            
            print(f"\n✅ 识别成功")
            print(f"  ⏱️  耗时: {recognition_time:.2f} 秒")
            print(f"  📊 识别到 {len(questions)} 道题目")
            
            for section in paper_structure.part_info:
                print(f"  📋 {section.part_title}: {len(section.subject_list)} 道题")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["recognition_time"] = time.time() - start_time
            
            print(f"\n❌ 识别失败")
            print(f"  错误: {e}")
            
            import traceback
            result["traceback"] = traceback.format_exc()
        
        return result
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """运行所有测试"""
        images = self.get_test_images()
        
        if not images:
            print(f"⚠️  未找到测试图片: {self.test_dir}")
            return []
        
        print(f"\n🔍 发现 {len(images)} 张测试图片")
        for img in images:
            print(f"  - {img.name}")
        
        results = []
        for image_path in images:
            result = await self.test_single_image(image_path)
            results.append(result)
            self.results.append(result)
        
        return results


# ==================== 报告生成 ====================

class TestReporter:
    """测试报告生成器"""
    
    @staticmethod
    def print_summary(results: List[Dict[str, Any]]):
        """打印测试摘要"""
        print(f"\n{'='*80}")
        print("📊 测试摘要")
        print(f"{'='*80}")
        
        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        failed = total - success
        
        total_questions = sum(r["total_questions"] for r in results if r["status"] == "success")
        avg_time = sum(r["recognition_time"] for r in results) / total if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        print(f"成功率: {success/total*100:.1f}%" if total > 0 else "N/A")
        print(f"平均耗时: {avg_time:.2f} 秒")
        print(f"总识别题目数: {total_questions}")
        
        print(f"\n{'-'*80}")
        print("详细结果")
        print(f"{'-'*80}")
        
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"\n{i}. {status_icon} {result['image_name']}")
            print(f"   状态: {result['status']}")
            print(f"   耗时: {result['recognition_time']:.2f} 秒")
            
            if result["status"] == "success":
                print(f"   题目数: {result['total_questions']}")
                if result.get("paper_structure"):
                    for section in result["paper_structure"]["sections"]:
                        print(f"     - {section['title']}: {section['question_count']} 道")
            else:
                print(f"   错误: {result['error']}")
    
    @staticmethod
    def save_json_report(results: List[Dict[str, Any]], output_path: Path):
        """保存 JSON 格式的报告"""
        report = {
            "test_time": datetime.now().isoformat(),
            "total_tests": len(results),
            "success_count": sum(1 for r in results if r["status"] == "success"),
            "failed_count": sum(1 for r in results if r["status"] == "failed"),
            "total_questions": sum(r["total_questions"] for r in results if r["status"] == "success"),
            "results": results
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON 报告已保存: {output_path}")
    
    @staticmethod
    def generate_html_report(results: List[Dict[str, Any]], output_path: Path):
        """生成 HTML 格式的测试报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>试卷识别测试报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .summary-item {{
            text-align: center;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .summary-item .value {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .summary-item .label {{
            color: #666;
            margin-top: 5px;
        }}
        .test-result {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-result.success {{
            border-left: 5px solid #4CAF50;
        }}
        .test-result.failed {{
            border-left: 5px solid #f44336;
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .test-title {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .status-badge {{
            padding: 5px 15px;
            border-radius: 15px;
            color: white;
            font-size: 0.9em;
        }}
        .status-badge.success {{
            background-color: #4CAF50;
        }}
        .status-badge.failed {{
            background-color: #f44336;
        }}
        .test-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }}
        .detail-item {{
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .detail-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .detail-value {{
            font-weight: bold;
            margin-top: 5px;
        }}
        .questions-list {{
            margin-top: 15px;
        }}
        .question-item {{
            padding: 10px;
            margin-bottom: 8px;
            background: #f9f9f9;
            border-left: 3px solid #2196F3;
            border-radius: 3px;
        }}
        .error-message {{
            padding: 15px;
            background: #ffebee;
            border-radius: 5px;
            color: #c62828;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1>📄 试卷识别测试报告</h1>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="value">{len(results)}</div>
                <div class="label">总测试数</div>
            </div>
            <div class="summary-item">
                <div class="value" style="color: #4CAF50;">{sum(1 for r in results if r["status"] == "success")}</div>
                <div class="label">成功</div>
            </div>
            <div class="summary-item">
                <div class="value" style="color: #f44336;">{sum(1 for r in results if r["status"] == "failed")}</div>
                <div class="label">失败</div>
            </div>
            <div class="summary-item">
                <div class="value">{sum(r["total_questions"] for r in results if r["status"] == "success")}</div>
                <div class="label">识别题目总数</div>
            </div>
            <div class="summary-item">
                <div class="value">{sum(r["recognition_time"] for r in results) / len(results) if results else 0:.2f}s</div>
                <div class="label">平均耗时</div>
            </div>
        </div>
    </div>
    
    <h2>详细结果</h2>
"""
        
        for i, result in enumerate(results, 1):
            status_class = result["status"]
            status_text = "成功" if status_class == "success" else "失败"
            
            html += f"""
    <div class="test-result {status_class}">
        <div class="test-header">
            <div class="test-title">{i}. {result['image_name']}</div>
            <span class="status-badge {status_class}">{status_text}</span>
        </div>
        
        <div class="test-details">
            <div class="detail-item">
                <div class="detail-label">识别耗时</div>
                <div class="detail-value">{result['recognition_time']:.2f} 秒</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">识别方式</div>
                <div class="detail-value">{result.get('method', 'unknown')}</div>
            </div>
"""
            
            if result["status"] == "success":
                html += f"""
            <div class="detail-item">
                <div class="detail-label">题目总数</div>
                <div class="detail-value">{result['total_questions']}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">图片尺寸</div>
                <div class="detail-value">{result['paper_structure']['width']} x {result['paper_structure']['height']}</div>
            </div>
"""
                
                html += """
        </div>
        
        <div class="questions-list">
            <h3>题目列表</h3>
"""
                
                for q in result["questions"]:
                    html += f"""
            <div class="question-item">
                <strong>题目 {q['index']}</strong> ({q['type']}) - {q['section_title']}<br>
                {q['question_preview']}
                {f"<br><em>选项数: {q['option_count']}</em>" if q['has_options'] else ""}
            </div>
"""
                
                html += """
        </div>
"""
            else:
                html += """
        </div>
"""
                if result.get("error"):
                    html += f"""
        <div class="error-message">
            <strong>错误信息:</strong><br>
            {result['error']}
        </div>
"""
            
            html += """
    </div>
"""
        
        html += f"""
    <div style="text-align: center; margin-top: 30px; color: #666;">
        <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ HTML 报告已保存: {output_path}")


# ==================== 主函数 ====================

async def main():
    """主测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="试卷识别自动化测试")
    parser.add_argument(
        "--test-dir",
        type=str,
        default=TEST_CONFIG["test_dir"],
        help="测试图片目录"
    )
    parser.add_argument(
        "--use-imgbb",
        action="store_true",
        help="使用 ImgBB 图床上传（需要配置 API Key）"
    )
    parser.add_argument(
        "--imgbb-key",
        type=str,
        default=IMGBB_API_KEY,
        help="ImgBB API Key"
    )
    parser.add_argument(
        "--use-base64",
        action="store_true",
        help="使用 base64 编码方式（不推荐，较慢）"
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="生成 HTML 格式的测试报告"
    )
    parser.add_argument(
        "--with-diagnose",
        action="store_true",
        help="同时测试批量诊断功能（需要较长时间）"
    )
    
    args = parser.parse_args()
    
    # 创建测试实例
    test = PaperRecognitionTest(
        test_dir=args.test_dir,
        use_imgbb=args.use_imgbb,
        imgbb_key=args.imgbb_key,
        use_local_server=not args.use_imgbb and not args.use_base64,
        use_base64=args.use_base64,
    )
    
    try:
        # 测试前准备
        test.setup()
        
        # 运行测试
        results = await test.run_all_tests()
        
        # 生成报告
        TestReporter.print_summary(results)
        
        # 保存 JSON 报告
        output_dir = Path(TEST_CONFIG["output_dir"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"test_report_{timestamp}.json"
        TestReporter.save_json_report(results, json_path)
        
        # 生成 HTML 报告（如果指定）
        if args.html_report:
            html_path = output_dir / f"test_report_{timestamp}.html"
            TestReporter.generate_html_report(results, html_path)
        
        print(f"\n{'='*80}")
        print("✅ 所有测试完成")
        print(f"{'='*80}\n")
        
    finally:
        # 测试后清理
        test.teardown()


if __name__ == "__main__":
    asyncio.run(main())

