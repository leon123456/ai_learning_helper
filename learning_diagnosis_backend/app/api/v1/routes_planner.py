# app/api/v1/routes_planner.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, List
from app.api import deps
from app.services.llm import LLMClient

router = APIRouter()

class PlannerRequest(BaseModel):
    mastery: Dict[str, int]  # {"一次函数": 60, "勾股定理": 90}

class DayPlan(BaseModel):
    day: int
    tasks: List[str]

class PlannerResponse(BaseModel):
    weak_points: List[str]
    seven_day_plan: List[DayPlan]

@router.post("/planner/generate", response_model=PlannerResponse)
async def generate_plan(
    req: PlannerRequest,
    llm: LLMClient = Depends(deps.get_llm_client)
):
    # TODO: 调用 Learning Planner Agent
    weak_points = [k for k, v in req.mastery.items() if v < 75]

    # 暂时 mock 一个简单计划
    plans = [
        DayPlan(day=1, tasks=[f"复习 {weak_points[0]} 的基础概念（10 分钟）",
                              f"完成 3 道 {weak_points[0]} 入门题"])
    ] if weak_points else []

    return PlannerResponse(weak_points=weak_points, seven_day_plan=plans)
