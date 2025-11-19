# app/schemas/diagnose.py

from typing import List, Optional
from pydantic import BaseModel


# =========================
#  题目结构（来自 OCR / Parser）
# =========================

class Problem(BaseModel):
    type: str                       # "choice", "fill", "solve", "proof", "short_answer"
    question: str                   # 题干
    options: Optional[List[str]] = None  # 选择题的选项
    knowledge_points: List[str] = []     # OCR 提取或 Parser 推断
    difficulty: str = "medium"           # easy/medium/hard
    correct_answer: Optional[str] = None # 题库中可能存在，也可能缺失（关键）


# =========================
#  诊断 API 输入结构
# =========================

class DiagnoseRequest(BaseModel):
    problem: Problem
    user_answer: str                # 用户作答原文


# =========================
#  诊断 API 输出结构
# =========================

class RecommendedPractice(BaseModel):
    knowledge: str
    difficulty: str
    count: int                      # 建议做几道


class DiagnoseResult(BaseModel):
    correct: bool
    correct_answer: str
    user_answer: str
    error_type: str
    analysis: str
    mastery_score: int
    next_action: str
    recommended_practice: List[RecommendedPractice]


# =========================
#  题目缓存结构（用于 LLM 自动求解）
# =========================

class CachedAnswer(BaseModel):
    question: str
    correct_answer: str
    llm_reason: str
    knowledge_points: List[str]
