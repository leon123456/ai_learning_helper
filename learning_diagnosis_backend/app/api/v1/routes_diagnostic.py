# app/api/v1/routes_diagnose.py

from fastapi import APIRouter, Depends
from app.schemas.diagnose import DiagnoseRequest, DiagnoseResult
from app.services.diagnostic import DiagnosticEngine
from app.api.deps import get_llm_client

router = APIRouter()


@router.post("/diagnose", response_model=DiagnoseResult)
async def diagnose_problem(
    req: DiagnoseRequest,
    llm = Depends(get_llm_client)
):
    """
    核心诊断接口：
    - 自动判断题库内题目
    - 自动求解题库外题目
    - 主观题 + 客观题混合模式
    - 自动缓存求解过的题目
    """
    engine = DiagnosticEngine(llm)
    result = await engine.diagnose(req)
    return result
