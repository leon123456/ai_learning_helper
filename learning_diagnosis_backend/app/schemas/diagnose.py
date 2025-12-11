# app/schemas/diagnose.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# =========================
#  题目结构（来自 OCR / Parser）
# =========================

class ProblemFigure(BaseModel):
    """题目配图信息"""
    type: str  # 图形类型：subject_pattern（题目配图）、table（表格）等
    x: int     # 左上角 X 坐标
    y: int     # 左上角 Y 坐标
    w: int     # 宽度
    h: int     # 高度
    description: Optional[str] = None  # 配图描述


class Problem(BaseModel):
    type: str                       # "choice", "fill", "solve", "proof", "short_answer"
    question: str                   # 题干
    options: Optional[List[str]] = None  # 选择题的选项
    knowledge_points: List[str] = []     # OCR 提取或 Parser 推断
    difficulty: str = "medium"           # easy/medium/hard
    correct_answer: Optional[str] = None # 题库中可能存在，也可能缺失（关键）
    
    # 配图信息（用于传递给 LLM）
    figures: List[ProblemFigure] = []  # 题目配图列表
    has_figure: bool = False           # 是否包含配图
    figure_description: Optional[str] = None  # 配图的文字描述（用于纯文本 LLM）
    
    def get_full_question(self) -> str:
        """获取完整题目文本（包含配图描述）"""
        if self.figure_description:
            return f"{self.question}\n\n【配图信息】\n{self.figure_description}"
        return self.question


# =========================
#  诊断 API 输入结构
# =========================

class DiagnoseRequest(BaseModel):
    problem: Problem
    user_answer: str                # 用户作答原文
    
    # 图片信息（用于 Vision 模型）
    image_url: Optional[str] = None       # 原始试卷图片 URL
    image_base64: Optional[str] = None    # 原始试卷图片 base64


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
