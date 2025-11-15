# app/api/v1/routes_diagnostic.py
from fastapi import APIRouter, Depends
from app.schemas.diagnostic import DiagnoseRequest, DiagnoseResponse, DiagnoseResult
from app.api import deps
from app.services.llm import LLMClient

router = APIRouter()

@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(
    req: DiagnoseRequest,
    llm: LLMClient = Depends(deps.get_llm_client)
):
    # TODO: 调用 Diagnostic Agent Prompt
    # 这部分暂时先用 mock 数据，之后替换为真正的 LLM 推理
    result = DiagnoseResult(
        correct=False,
        mastery_score=40,
        error_type=["概念不清"],
        reason="学生没有正确理解一次函数的代入求值方法。",
        next_action="建议先复习一次函数的定义和代入计算，再做 3 道类似练习题。"
    )

    return DiagnoseResponse(result=result)
