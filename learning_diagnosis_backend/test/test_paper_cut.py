#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阿里云 EduPaperCut（试卷切题识别）API

支持两种调用方式：
1. API 市场方式 - 使用 APPCODE 认证
2. 官方 SDK 方式 - 使用 AccessKey 认证

API 市场文档: https://market.aliyun.com/products/57124001/cmapi00054877.html
官方 SDK 文档: https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeedupapercut
"""

import asyncio
import base64
import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime
import urllib3

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(env_path)


def test_paper_cut_market_api(image_path: Path, appcode: str = None):
    """
    使用 API 市场方式测试 EduPaperCut API
    
    参考官方 demo，使用 APPCODE 认证方式调用 API 市场接口
    
    Args:
        image_path: 测试图片路径
        appcode: 阿里云 API 市场的 APPCODE（如果不提供，从环境变量 ALIYUN_APPCODE 读取）
    
    预期输入:
        - image_path: 存在的图片文件路径（jpg/png/bmp，base64 后 < 25M）
        - appcode: 有效的阿里云 API 市场 APPCODE
    
    预期输出:
        - 成功: 返回包含题目切分结果的字典
        - 失败: 返回 None
    """
    print("=" * 80)
    print("🔪 测试阿里云 EduPaperCut（试卷切题识别）- API 市场方式")
    print("=" * 80)
    print(f"📄 测试图片: {image_path}")
    
    # 获取 APPCODE（优先使用传入参数，其次使用 settings 配置，最后使用环境变量）
    if not appcode:
        try:
            from app.core.config import settings
            appcode = settings.ALIYUN_APPCODE
        except ImportError:
            pass
    if not appcode:
        appcode = os.environ.get("ALIYUN_APPCODE", "")
    
    if not appcode:
        print("❌ 未配置阿里云 APPCODE，请设置：")
        print("   1. 在 .env 中添加: ALIYUN_APPCODE=你的AppCode")
        print("   2. 或者在调用时传入 appcode 参数")
        print("\n💡 获取 APPCODE 的方式：")
        print("   访问 https://market.aliyun.com/products/57124001/cmapi00054877.html")
        print("   购买服务后，在控制台 -> 云市场 -> 已购买的服务 中查看 APPCODE")
        return None
    
    print(f"✅ 使用 APPCODE: {appcode[:8]}...")
    
    # 读取图片
    print(f"\n📦 读取图片...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    print(f"   图片大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
    print(f"   Base64 长度: {len(image_base64)} 字符")
    
    # API 配置
    host = 'https://subject2.market.alicloudapi.com'
    path = '/educationservice/papercut'
    url = host + path
    
    # 请求头
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'APPCODE ' + appcode
    }
    
    # 请求体 - 根据官方文档构建
    # paperType: question(切题) / answer(切答案)
    # templateType: Math(数学), Chinese(语文), English(英语) 等
    request_body = {
        "imgList": [image_base64],      # 图像 base64 数组（与 urlList 二选一）
        "paperType": "question",         # 切题类型：question=切题，answer=切答案
        "templateType": "Math",          # 年级学科：Math=数学，详见下方注释
        "rotate": False,                 # 是否需要自动旋转，默认不需要
        "image_correction": True,        # 是否做图片矫正，默认不做
    }
    # templateType 可选值:
    # - default: 默认
    # - Math: 数学
    # - PrimarySchool_Math: 小学数学
    # - JHighSchool_Math: 初中数学
    # - Chinese: 语文
    # - PrimarySchool_Chinese: 小学语文
    # - JHighSchool_Chinese: 初中语文
    # - English: 英语
    # - PrimarySchool_English: 小学英语
    # - JHighSchool_English: 初中英语
    # - Physics: 物理
    # - JHighSchool_Physics: 初中物理
    # - Chemistry: 化学
    # - JHighSchool_Chemistry: 初中化学
    # - Biology: 生物
    # - JHighSchool_Biology: 初中生物
    # - History: 历史
    # - JHighSchool_History: 初中历史
    # - Geography: 地理
    # - JHighSchool_Geography: 初中地理
    # - Politics: 政治
    # - JHighSchool_Politics: 初中政治
    
    print(f"\n🔍 调用 API 市场接口...")
    print(f"   URL: {url}")
    print(f"   paperType: {request_body['paperType']}")
    print(f"   templateType: {request_body['templateType']}")
    
    start_time = time.time()
    
    try:
        # 使用 urllib3 发送请求
        http = urllib3.PoolManager()
        post_data = json.dumps(request_body)
        
        response = http.request(
            'POST', 
            url, 
            body=post_data.encode('utf-8'), 
            headers=headers,
            timeout=urllib3.Timeout(connect=60, read=180)  # 连接超时60s，读取超时180s
        )
        
        elapsed = time.time() - start_time
        
        # 解析响应
        content = response.data.decode('utf-8')
        status_code = response.status
        
        print(f"\n📥 响应状态码: {status_code}")
        print(f"   耗时: {elapsed:.2f} 秒")
        
        if status_code == 200:
            result = json.loads(content)
            print(f"✅ API 调用成功！")
            print(f"\n📊 响应内容预览（前 2000 字符）:")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
            
            # 分析结果
            if "Data" in result:
                try:
                    data = json.loads(result["Data"]) if isinstance(result["Data"], str) else result["Data"]
                    if "page_list" in data:
                        page_count = len(data["page_list"])
                        total_questions = sum(
                            len(page.get("subject_list", [])) 
                            for page in data["page_list"]
                        )
                        print(f"\n📋 识别结果统计:")
                        print(f"   页面数量: {page_count}")
                        print(f"   题目总数: {total_questions}")
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"\n⚠️ 解析 Data 字段失败: {e}")
            
            # 保存结果
            save_result(image_path, result, elapsed, "market_api")
            return result
            
        else:
            print(f"❌ API 调用失败！")
            print(f"   响应内容: {content}")
            
            # 常见错误码说明
            if status_code == 403:
                print("\n💡 可能原因：")
                print("   - APPCODE 无效或已过期")
                print("   - 服务未购买或已到期")
            elif status_code == 400:
                print("\n💡 可能原因：")
                print("   - 请求参数格式错误")
                print("   - 图片格式不支持")
            elif status_code == 500:
                print("\n💡 可能原因：")
                print("   - 服务器内部错误")
                print("   - 图片内容无法识别")
            
            return None
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 请求异常（耗时: {elapsed:.2f} 秒）")
        print(f"   错误: {e}")
        
        import traceback
        traceback.print_exc()
        
        return None


async def test_paper_cut_sdk(image_path: Path):
    """
    使用官方 SDK 方式测试 EduPaperCut API
    
    使用阿里云官方 OCR SDK，需要 AccessKey 认证
    
    关键点（参考 aliyun_paper_ocr.py 的成功实现）：
    1. 使用 RecognizeEduPaperCutRequest 类（不是通用的 OpenApiRequest）
    2. 使用 recognize_edu_paper_cut_with_options_async 方法
    3. 传递 body 参数为二进制数据（不是 base64 字符串）
    
    Args:
        image_path: 测试图片路径
    
    预期输入:
        - image_path: 存在的图片文件路径
        - 环境变量 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET 已配置
    
    预期输出:
        - 成功: 返回包含题目切分结果的字典
        - 失败: 返回 None
    """
    print("=" * 80)
    print("🔪 测试阿里云 EduPaperCut（试卷切题识别）- 官方 SDK 方式")
    print("=" * 80)
    print(f"📄 测试图片: {image_path}")
    
    from app.core.config import settings
    
    # 检查配置
    if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
        print("❌ 未配置阿里云 AccessKey，请在 .env 中设置：")
        print("   ALIYUN_ACCESS_KEY_ID=你的AccessKeyId")
        print("   ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret")
        return None
    
    print(f"✅ 使用阿里云 AccessKey（ID: {settings.ALIYUN_ACCESS_KEY_ID[:8]}...）")
    
    # 读取图片（关键：body 需要的是二进制数据，不是 base64）
    print(f"\n📦 读取图片...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    print(f"   图片大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
    
    print(f"\n🔍 调用 EduPaperCut API (使用 SDK)...")
    start_time = time.time()
    
    try:
        from alibabacloud_ocr_api20210707.client import Client as OcrApiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
        from alibabacloud_tea_util import models as util_models
        
        # 创建客户端配置
        config = open_api_models.Config(
            access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
            access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
        )
        config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
        client = OcrApiClient(config)
        
        # 使用专门的 RecognizeEduPaperCutRequest（类似于 RecognizeEduPaperStructedRequest）
        request = ocr_api_20210707_models.RecognizeEduPaperCutRequest()
        
        # 关键：body 字段需要的是图片的原始二进制数据（和 RecognizeEduPaperStructed 一样）
        request.body = image_bytes
        
        # 设置必需参数
        request.cut_type = "question"  # CutType: question(切题) / answer(切答案)
        request.image_type = "scan"    # ImageType: scan(扫描件) / photo(实拍图) - 必需参数！
        request.subject = "Math"       # 学科类型
        
        # 调试输出 - 确认参数正确设置
        print(f"   ✓ body: {type(request.body).__name__}, {len(request.body)} 字节")
        print(f"   ✓ cut_type: {request.cut_type}")
        print(f"   ✓ image_type: {request.image_type}")
        print(f"   ✓ subject: {request.subject}")
        
        # 设置运行时选项
        runtime = util_models.RuntimeOptions(
            read_timeout=180000,   # 读取超时 180 秒
            connect_timeout=60000, # 连接超时 60 秒
            autoretry=True,        # 启用自动重试
            max_attempts=3,        # 最多重试 3 次
        )
        
        # 调用 API（使用专门的方法，类似 recognize_edu_paper_structed_with_options_async）
        response = await client.recognize_edu_paper_cut_with_options_async(request, runtime)
        elapsed = time.time() - start_time
        
        print(f"✅ API 调用成功！耗时: {elapsed:.2f} 秒")
        
        # 解析响应
        if not response or not response.body:
            raise Exception("API 返回空响应")
        
        # 解析返回的 JSON 字符串
        data_str = response.body.data
        if not data_str:
            raise Exception("API 返回的 data 为空")
        
        data = json.loads(data_str)
        
        print(f"\n📊 响应数据统计:")
        if "page_list" in data:
            page_count = len(data["page_list"])
            total_questions = sum(
                len(page.get("subject_list", [])) 
                for page in data["page_list"]
            )
            print(f"   页面数量: {page_count}")
            print(f"   题目总数: {total_questions}")
        
        print(f"\n📊 响应内容预览（前 2000 字符）:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        
        # 保存结果
        save_result(image_path, data, elapsed, "sdk")
        return data
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ API 调用失败（耗时: {elapsed:.2f} 秒）")
        print(f"   错误: {e}")
        
        if hasattr(e, 'message'):
            print(f"   消息: {e.message}")
        if hasattr(e, 'data') and e.data:
            recommend = e.data.get("Recommend", "")
            if recommend:
                print(f"   诊断地址: {recommend}")
        
        import traceback
        traceback.print_exc()
        
        return None


def save_result(image_path: Path, result: dict, elapsed: float, method: str):
    """保存测试结果到文件"""
    result_dir = Path(__file__).parent / "test_results"
    result_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = result_dir / f"paper_cut_{method}_{timestamp}.json"
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "image": str(image_path.name),
            "method": method,
            "api": "EduPaperCut",
            "elapsed_seconds": elapsed,
            "response": result,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {result_file}")


def main():
    """主函数 - 同步版本，使用 API 市场方式"""
    # 测试图片路径
    test_image = Path(__file__).parent / "test_png" / "2025gaokao1.png"
    
    if not test_image.exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 使用 API 市场方式测试
    result = test_paper_cut_market_api(test_image)
    
    if result:
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
    else:
        print("\n" + "=" * 80)
        print("❌ 测试失败，请检查配置和网络")


async def main_async():
    """主函数 - 异步版本，使用官方 SDK 方式"""
    # 测试图片路径
    test_image = Path(__file__).parent / "test_png" / "2025gaokao1.png"
    
    if not test_image.exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 使用官方 SDK 方式测试
    await test_paper_cut_sdk(test_image)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试阿里云 EduPaperCut API")
    parser.add_argument(
        "--method", 
        choices=["market", "sdk"], 
        default="market",
        help="选择调用方式: market=API市场, sdk=官方SDK (默认: market)"
    )
    parser.add_argument(
        "--appcode",
        type=str,
        default=None,
        help="阿里云 API 市场的 APPCODE（可选，也可通过环境变量 ALIYUN_APPCODE 设置）"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="测试图片路径（可选，默认使用 test_png/2025gaokao1.png）"
    )
    
    args = parser.parse_args()
    
    # 确定测试图片
    if args.image:
        test_image = Path(args.image)
    else:
        test_image = Path(__file__).parent / "test_png" / "2025gaokao1.png"
    
    if not test_image.exists():
        print(f"❌ 测试图片不存在: {test_image}")
        sys.exit(1)
    
    if args.method == "market":
        # API 市场方式（同步）
        result = test_paper_cut_market_api(test_image, appcode=args.appcode)
    else:
        # 官方 SDK 方式（异步）
        asyncio.run(main_async())
