# app/schemas/ocr.py
from pydantic import BaseModel
from typing import List, Optional

class OCRRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None

class ParsedProblem(BaseModel):
    type: str
    question: str
    options: Optional[List[str]] = None
    knowledge_points: List[str] = []
    difficulty: str = "medium"

class OCRResponse(BaseModel):
    raw_text: str
    problems: List[ParsedProblem]
