# app/api/v1/routes_paper.py

"""
试卷相关的 API 路由

提供试卷结构化识别和批量诊断功能
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.paper import (
    PaperOCRRequest,
    PaperOCRResponse,
    BatchDiagnoseRequest,
    BatchDiagnoseResponse,
)
from app.api import deps
from app.services.llm import LLMClient
from app.services.paper_diagnostic import PaperDiagnosticService
import traceback


router = APIRouter()


@router.post("/paper/recognize", response_model=PaperOCRResponse)
async def recognize_paper(
    req: PaperOCRRequest,
    llm: LLMClient = Depends(deps.get_llm_client),
):
    """
    试卷结构化识别
    
    功能：
    - 上传整张试卷图片（URL 或 base64）
    - 调用阿里云 RecognizeEduPaperStructed API
    - 自动切题、识别题干、选项、公式
    - 返回题目坐标（可用于前端高亮）
    - 支持整页、拍照、教辅、练习册
    
    请求示例：
    ```json
    {
        "image_url": "https://example.com/paper.jpg"
    }
    ```
    
    响应示例：
    ```json
    {
        "paper_structure": {
            "page_id": 1,
            "width": 2377,
            "height": 3442,
            "part_info": [...],
            "figure": [...]
        },
        "questions": [
            {
                "index": 1,
                "type": "choice",
                "question": "下列各组数据中...",
                "options": ["A.前2s末、第2s末、第3s初", ...],
                "position": [[{"x": 170, "y": 417}, ...]],
                "section_title": "选择题"
            }
        ],
        "total_questions": 10
    }
    ```
    """
    # 校验输入
    if not req.image_url and not req.image_base64:
        raise HTTPException(
            status_code=400, 
            detail="需要提供 image_url 或 image_base64"
        )
    
    try:
        # 创建试卷诊断服务
        service = PaperDiagnosticService(llm)
        
        # 识别并解析试卷
        paper_structure, questions = await service.recognize_and_parse_paper(
            image_url=req.image_url,
            image_base64=req.image_base64,
        )
        
        # 返回结果
        return PaperOCRResponse(
            paper_structure=paper_structure,
            questions=questions,
            total_questions=len(questions),
            figures=paper_structure.figure or []  # 提取配图列表
        )
    
    except ValueError as e:
        # 配置错误或参数错误
        raise HTTPException(
            status_code=400,
            detail=f"参数错误: {str(e)}"
        )
    except ImportError as e:
        # SDK 未安装
        raise HTTPException(
            status_code=500,
            detail=f"依赖未安装: {str(e)}"
        )
    except Exception as e:
        # 其他错误
        error_msg = str(e)
        error_type = type(e).__name__
        
        # 提供更友好的错误提示
        if "api" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            raise HTTPException(
                status_code=500,
                detail=f"阿里云 API 调用失败: {error_msg}. 请检查 AccessKey 配置和 RAM 权限。"
            )
        elif "image" in error_msg.lower() or "url" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"图片处理失败: {error_msg}. 请检查图片 URL 是否可访问或 base64 格式是否正确。"
            )
        else:
            # 记录详细堆栈信息
            traceback_str = traceback.format_exc()
            print(f"试卷识别失败:\n{traceback_str}")
            
            raise HTTPException(
                status_code=500,
                detail=f"试卷识别失败 ({error_type}): {error_msg}"
            )


@router.post("/paper/batch-diagnose", response_model=BatchDiagnoseResponse)
async def batch_diagnose_paper(
    req: BatchDiagnoseRequest,
    llm: LLMClient = Depends(deps.get_llm_client),
):
    """
    试卷批量诊断
    
    功能：
    - 对整张试卷的所有题目进行批量诊断
    - 自动判断每道题的对错
    - 生成每道题的详细诊断报告
    - 统计整体正确率、掌握度
    - 按题型统计
    - 识别薄弱知识点
    - 提供学习建议
    
    使用流程：
    1. 先调用 `/paper/recognize` 识别试卷，获得题目列表
    2. 用户作答后，将题目列表和答案一起提交到本接口
    
    请求示例：
    ```json
    {
        "questions": [
            {
                "index": 1,
                "type": "choice",
                "question": "下列各组数据中...",
                "options": ["A.前2s末、第2s末、第3s初", ...],
                "position": [...]
            }
        ],
        "answers": [
            {
                "question_index": 1,
                "user_answer": "A"
            }
        ]
    }
    ```
    
    响应示例：
    ```json
    {
        "results": [
            {
                "question_index": 1,
                "question": {...},
                "diagnose_result": {
                    "correct": true,
                    "correct_answer": "A",
                    "user_answer": "A",
                    "error_type": "无",
                    "analysis": "...",
                    "mastery_score": 95,
                    "next_action": "...",
                    "recommended_practice": [...]
                }
            }
        ],
        "summary": {
            "total_questions": 10,
            "answered_questions": 10,
            "correct_count": 8,
            "wrong_count": 2,
            "unanswered_count": 0,
            "accuracy": 80.0,
            "average_mastery": 75.5,
            "stats_by_type": {...},
            "weak_knowledge_points": [...],
            "overall_suggestion": "..."
        }
    }
    ```
    """
    # 校验输入
    if not req.questions:
        raise HTTPException(
            status_code=400,
            detail="题目列表不能为空"
        )
    
    try:
        # 创建试卷诊断服务
        service = PaperDiagnosticService(llm)
        
        # 批量诊断
        result = await service.batch_diagnose(
            questions=req.questions,
            answers=req.answers,
        )
        
        return result
    
    except ValueError as e:
        # 参数错误
        raise HTTPException(
            status_code=400,
            detail=f"参数错误: {str(e)}"
        )
    except Exception as e:
        # 其他错误
        error_msg = str(e)
        error_type = type(e).__name__
        
        # 记录详细堆栈信息
        traceback_str = traceback.format_exc()
        print(f"批量诊断失败:\n{traceback_str}")
        
        # 提供更友好的错误提示
        if "api" in error_msg.lower() or "key" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail=f"LLM API 调用失败: {error_msg}. 请检查 API 配置和网络连接。"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"批量诊断失败 ({error_type}): {error_msg}"
            )

