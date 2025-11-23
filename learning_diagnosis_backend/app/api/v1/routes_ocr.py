# app/api/v1/routes_ocr.py

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ocr import OCRRequest, OCRResponse
from app.api import deps
from app.services.llm import LLMClient
from app.services.ocr import run_ocr_pipeline
import traceback

router = APIRouter()


@router.post("/ocr/parse", response_model=OCRResponse)
async def parse_image(
    req: OCRRequest,
    llm: LLMClient = Depends(deps.get_llm_client),
):
    # 简单校验
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="需要提供 image_url 或 image_base64")

    try:
        raw_text, problems = await run_ocr_pipeline(
            llm=llm,
            image_url=req.image_url,
            image_base64=req.image_base64,
        )
        return OCRResponse(raw_text=raw_text, problems=problems)
    
    except ValueError as e:
        # 配置错误或参数错误
        raise HTTPException(
            status_code=400,
            detail=f"参数错误: {str(e)}"
        )
    except Exception as e:
        # 其他错误，记录详细堆栈信息
        error_msg = str(e)
        error_type = type(e).__name__
        
        # 如果是 API 相关错误，提供更友好的提示
        if "api" in error_msg.lower() or "key" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail=f"LLM API 调用失败: {error_msg}. 请检查 API 配置和网络连接。"
            )
        elif "image" in error_msg.lower() or "url" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"图片处理失败: {error_msg}. 请检查图片 URL 是否可访问。"
            )
        else:
            # 其他未知错误
            import traceback
            traceback_str = traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"OCR 处理失败 ({error_type}): {error_msg}"
            )
