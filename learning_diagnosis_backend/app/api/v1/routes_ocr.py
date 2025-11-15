# app/api/v1/routes_ocr.py
from fastapi import APIRouter, Depends
from app.schemas.ocr import OCRRequest, OCRResponse, ParsedProblem
from app.api import deps
from app.services.llm import LLMClient

router = APIRouter()

@router.post("/ocr/parse", response_model=OCRResponse)
async def parse_image(
    req: OCRRequest,
    llm: LLMClient = Depends(deps.get_llm_client)
):
    # TODO: 1. 调用 OCR（之后可以接 vision 模型或第三方OCR）
    # 这里先 mock 一段 raw_text
    raw_text = "y = 2x + 1 是一个一次函数，求当 x = 3 时 y 的值。"

    # TODO: 2. 调用 Problem Parser Agent（使用 /prompt/parser.md）
    # 目前先 mock 一个 problem
    problem = ParsedProblem(
        type="fill",
        question=raw_text,
        options=None,
        knowledge_points=["一次函数"],
        difficulty="easy",
    )

    return OCRResponse(raw_text=raw_text, problems=[problem])
