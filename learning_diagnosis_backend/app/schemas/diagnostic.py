# app/schemas/diagnostic.py
from pydantic import BaseModel
from typing import List, Optional

class DiagnoseRequest(BaseModel):
    problem: str
    standard_answer: Optional[str] = None
    student_answer: str
    knowledge_points: List[str] = []

class DiagnoseResult(BaseModel):
    correct: bool
    mastery_score: int
    error_type: List[str]
    reason: str
    next_action: str

class DiagnoseResponse(BaseModel):
    result: DiagnoseResult
