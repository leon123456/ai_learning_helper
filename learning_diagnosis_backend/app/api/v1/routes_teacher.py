# app/api/v1/routes_teacher.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api import deps
from app.services.llm import LLMClient

router = APIRouter()

class TeacherChatRequest(BaseModel):
    question: str
    context: List[str] = []   # 可附带题目、学生之前的错误等

class TeacherChatResponse(BaseModel):
    reply: str

@router.post("/teacher/chat", response_model=TeacherChatResponse)
async def teacher_chat(
    req: TeacherChatRequest,
    llm: LLMClient = Depends(deps.get_llm_client)
):
    # TODO: 从 prompt/teacher.md 读取 AI 教师 System Prompt
    # 然后调用 llm.chat(...)
    reply = "这是老师模式的占位回复。后面会变成真正的分步骤讲解和提示。"
    return TeacherChatResponse(reply=reply)
