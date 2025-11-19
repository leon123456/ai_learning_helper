# app/api/v1/routes_ocr.py

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ocr import OCRRequest, OCRResponse
from app.api import deps
from app.services.llm import LLMClient
from app.services.ocr import run_ocr_pipeline

router = APIRouter()


@router.post("/ocr/parse", response_model=OCRResponse)
async def parse_image(
    req: OCRRequest,
    llm: LLMClient = Depends(deps.get_llm_client),
):
    # 简单校验
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="需要提供 image_url 或 image_base64")

    raw_text, problems = await run_ocr_pipeline(
        llm=llm,
        image_url=req.image_url,
        image_base64=req.image_base64,
    )

    return OCRResponse(raw_text=raw_text, problems=problems)
