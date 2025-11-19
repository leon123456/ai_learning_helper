# app/api/v1/routes_teacher.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api import deps
from app.services.llm import LLMClient

router = APIRouter()


class TeacherChatRequest(BaseModel):
    question: str
    context: List[str] = []


class TeacherChatResponse(BaseModel):
    reply: str


@router.post("/teacher/chat", response_model=TeacherChatResponse)
async def teacher_chat(
    req: TeacherChatRequest,
    llm: LLMClient = Depends(deps.get_llm_client)
):
    system_prompt = """
你是一位耐心的数学老师，你会用清晰易懂的方式回答学生的问题。
不要输出太多内容。
"""

    reply = await llm.chat(
        system_prompt=system_prompt,
        user_message=req.question,
        model=None,  # 自动选用 Azure 模型
    )

    return TeacherChatResponse(reply=reply)
