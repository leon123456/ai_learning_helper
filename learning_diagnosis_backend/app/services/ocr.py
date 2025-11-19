### 2.2 新建服务文件：`app/services/ocr.py`

# app/services/ocr.py

from pathlib import Path
from typing import List, Tuple

from app.services.llm import LLMClient
from app.schemas.ocr import ParsedProblem


def _load_parser_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "prompt" / "parser.md"
    return prompt_path.read_text(encoding="utf-8")


async def run_ocr_pipeline(
    llm: LLMClient,
    image_url: str | None = None,
    image_base64: str | None = None,
) -> Tuple[str, List[ParsedProblem]]:
    """
    整体流程：
    1. 使用 gpt-4o 的 vision 能力从图片中提取题目文本（raw_text）
    2. 使用 Parser Agent 将 raw_text 解析为结构化题目列表
    3. 返回 raw_text + ParsedProblem 列表
    """
    # 1. OCR：从图片中提取文字
    ocr_prompt = "请将图片中的题目内容完整、清晰地转写成纯文本，不要添加额外说明。"
    raw_text = await llm.ocr_with_image(
        prompt=ocr_prompt,
        image_url=image_url,
        image_base64=image_base64,
        temperature=0.0,
    )

    # 2. 题目结构化解析
    parser_prompt = _load_parser_prompt()
    parser_result = await llm.chat_json(
        system_prompt=parser_prompt,
        user_message=raw_text,
        model=None,  # 使用默认模型（对于 azure 即 gpt-4o-2）
    )

    problems: List[ParsedProblem] = []

    if isinstance(parser_result, dict) and "problems" in parser_result:
        for item in parser_result["problems"]:
            try:
                problems.append(ParsedProblem(**item))
            except Exception:
                # 某个题目字段不完整时，跳过它
                continue

    # 兜底：如果解析失败或无题目，就用整段文本做一个兜底题目
    if not problems:
        problems.append(
            ParsedProblem(
                type="short_answer",
                question=raw_text.strip(),
                options=None,
                knowledge_points=[],
                difficulty="medium",
            )
        )

    return raw_text, problems
