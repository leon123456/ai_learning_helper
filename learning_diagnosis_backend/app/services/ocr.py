### 2.2 新建服务文件：`app/services/ocr.py`

# app/services/ocr.py

from pathlib import Path
from typing import List, Tuple, Optional

from app.services.llm import LLMClient
from app.schemas.ocr import ParsedProblem
from app.core.config import settings


def _load_parser_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "prompt" / "parser.md"
    return prompt_path.read_text(encoding="utf-8")


async def _ocr_with_llm(
    llm: LLMClient,
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> str:
    """使用 LLM vision 进行 OCR 识别"""
    ocr_prompt = "请将图片中的题目内容完整、清晰地转写成纯文本，不要添加额外说明。"
    return await llm.ocr_with_image(
        prompt=ocr_prompt,
        image_url=image_url,
        image_base64=image_base64,
        temperature=0.0,
    )


async def _ocr_with_aliyun(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> str:
    """使用阿里云 OCR 进行识别"""
    from app.services.aliyun_ocr import recognize_with_aliyun
    return await recognize_with_aliyun(image_url=image_url, image_base64=image_base64)


async def run_ocr_pipeline(
    llm: LLMClient,
    image_url: str | None = None,
    image_base64: str | None = None,
) -> Tuple[str, List[ParsedProblem]]:
    """
    整体流程：
    1. 使用 OCR 从图片中提取题目文本（raw_text）
       - 支持 LLM vision 或阿里云 OCR
    2. 使用 Parser Agent 将 raw_text 解析为结构化题目列表
    3. 返回 raw_text + ParsedProblem 列表
    """
    # 1. OCR：从图片中提取文字
    print("\n" + "="*80)
    print("🔍 OCR 识别中...")
    print("="*80)
    
    ocr_provider = settings.OCR_PROVIDER.lower()
    raw_text = ""
    ocr_used = ""
    
    # 根据配置选择 OCR 提供者
    if ocr_provider == "aliyun":
        # 只使用阿里云
        print("📡 使用阿里云 OCR...")
        try:
            raw_text = await _ocr_with_aliyun(image_url=image_url, image_base64=image_base64)
            ocr_used = "阿里云 OCR"
        except Exception as e:
            print(f"❌ 阿里云 OCR 失败: {e}")
            raise
    elif ocr_provider == "llm":
        # 只使用 LLM
        print("🤖 使用 LLM Vision...")
        raw_text = await _ocr_with_llm(llm, image_url=image_url, image_base64=image_base64)
        ocr_used = "LLM Vision"
    else:  # auto 模式：优先阿里云，失败则回退 LLM
        print("🔄 自动模式：优先尝试阿里云 OCR...")
        try:
            raw_text = await _ocr_with_aliyun(image_url=image_url, image_base64=image_base64)
            ocr_used = "阿里云 OCR"
            print("✅ 阿里云 OCR 识别成功")
        except Exception as e:
            print(f"⚠️  阿里云 OCR 失败: {e}")
            print("🔄 回退到 LLM Vision...")
            try:
                raw_text = await _ocr_with_llm(llm, image_url=image_url, image_base64=image_base64)
                ocr_used = "LLM Vision (回退)"
            except Exception as e2:
                print(f"❌ LLM Vision 也失败: {e2}")
                raise Exception(f"所有 OCR 提供者都失败。阿里云: {e}，LLM: {e2}")
    
    print(f"\n📝 OCR 识别结果（使用 {ocr_used}）：")
    print("-"*80)
    print(raw_text)
    print("-"*80)
    print(f"文本长度: {len(raw_text)} 字符\n")

    # 2. 题目结构化解析
    parser_prompt = _load_parser_prompt()
    parser_result = await llm.chat_json(
        system_prompt=parser_prompt,
        user_message=raw_text,
        model=None,  # 使用默认模型（对于 azure 即 gpt-4o-2）
    )

    problems: List[ParsedProblem] = []

    print("🔧 正在解析题目结构...")
    if isinstance(parser_result, dict) and "problems" in parser_result:
        for item in parser_result["problems"]:
            try:
                problems.append(ParsedProblem(**item))
            except Exception:
                # 某个题目字段不完整时，跳过它
                continue

    # 兜底：如果解析失败或无题目，就用整段文本做一个兜底题目
    if not problems:
        print("⚠️  解析失败，使用兜底方案（将整段文本作为一道题）")
        problems.append(
            ParsedProblem(
                type="short_answer",
                question=raw_text.strip(),
                options=None,
                knowledge_points=[],
                difficulty="medium",
            )
        )
    
    print(f"\n✅ 解析完成，共识别到 {len(problems)} 道题目")
    print("="*80)
    for i, problem in enumerate(problems, 1):
        print(f"\n📋 题目 {i}:")
        print(f"   类型: {problem.type}")
        print(f"   题干: {problem.question[:100]}{'...' if len(problem.question) > 100 else ''}")
        if problem.options:
            print(f"   选项: {problem.options}")
        if problem.knowledge_points:
            print(f"   知识点: {problem.knowledge_points}")
        print(f"   难度: {problem.difficulty}")
    print("="*80 + "\n")

    return raw_text, problems
