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
    ocr_prompt = "请将图片中的题目内容完整、清晰地转写成纯文本，包括文字和几何图形的描述。如果有几何图形，请详细描述图形的结构、点的标注、线段关系等。"
    return await llm.ocr_with_image(
        prompt=ocr_prompt,
        image_url=image_url,
        image_base64=image_base64,
        temperature=0.2,  # 使用 0.2 以获得更稳定的结果
    )


async def _ocr_with_aliyun(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> str:
    """使用阿里云 OCR 进行识别"""
    from app.services.aliyun_ocr import recognize_with_aliyun
    return await recognize_with_aliyun(image_url=image_url, image_base64=image_base64)


async def _enhance_with_vision(
    llm: LLMClient,
    ocr_text: str,
    image_url: str | None = None,
    image_base64: str | None = None,
) -> str:
    """
    使用 GPT Vision 增强 OCR 结果，特别是识别几何图形
    
    Args:
        llm: LLM客户端
        ocr_text: OCR识别的文字
        image_url: 图片URL
        image_base64: Base64编码的图片
        
    Returns:
        增强后的文本（包含图形描述）
    """
    print("\n" + "="*80)
    print("🎨 使用 GPT Vision 分析几何图形...")
    print("="*80)
    
    vision_prompt = f"""你是一个数学题目分析专家。我给你一张数学题目的图片，已经通过 OCR 识别出了文字部分。

OCR 识别的文字：
{ocr_text}

现在请你重点分析图片中的**几何图形**部分（如果有的话）。

请按照以下格式输出：

【几何图形描述】
（如果图片中有几何图形）
- 图形类型：描述是什么图形（如三角形、四边形、圆等）
- 点的标注：列出所有可见的点标记（如A、B、C、D、E等）
- 点的位置关系：描述点之间的位置关系（如"点B、A、E在同一条直线上"）
- 线段和角：描述主要的线段和角度关系
- 其他特征：其他重要的几何特征

如果图片中**没有几何图形**，只有文字，请直接输出：无几何图形
"""
    
    try:
        # 使用 GPT Vision 分析图形
        vision_result = await llm.ocr_with_image(
            prompt=vision_prompt,
            image_url=image_url,
            image_base64=image_base64,
            temperature=0.2,
        )
        
        print("✅ GPT Vision 分析完成")
        print(f"📐 图形描述：\n{vision_result}\n")
        print("="*80)
        
        # 如果有图形描述，追加到 OCR 文本后
        if "无几何图形" not in vision_result and vision_result.strip():
            enhanced_text = f"{ocr_text}\n\n{vision_result}"
            return enhanced_text
        else:
            print("ℹ️  图片中没有几何图形或 Vision 未识别到")
            return ocr_text
            
    except Exception as e:
        print(f"⚠️  GPT Vision 分析失败: {e}")
        print("继续使用原始 OCR 文本")
        return ocr_text


async def run_ocr_pipeline(
    llm: LLMClient,
    image_url: str | None = None,
    image_base64: str | None = None,
    use_vision_enhancement: bool = True,  # 新增参数：是否使用 Vision 增强
) -> Tuple[str, List[ParsedProblem]]:
    """
    完整的 OCR 识别 + 解析流程
    
    步骤：
    1. 使用 OCR 提取文字（阿里云或 LLM）
    2. 如果使用阿里云，用 GPT Vision 补充识别几何图形
    3. 使用 Parser Agent 解析题目结构
    
    Args:
        llm: LLM客户端
        image_url: 图片URL
        image_base64: Base64编码的图片
        use_vision_enhancement: 是否使用 GPT Vision 增强（识别几何图形）
        
    Returns:
        (raw_text, problems): 原始识别文本和解析后的题目列表
    """
    print("\n" + "="*80)
    print("🔍 OCR 识别流程开始...")
    print("="*80)
    
    ocr_provider = settings.OCR_PROVIDER.lower()
    raw_text = ""
    ocr_used = ""
    
    # ========== 第一步：OCR 文字识别 ==========
    if ocr_provider == "aliyun":
        # 只使用阿里云
        print("📡 使用阿里云 OCR 识别文字...")
        try:
            raw_text = await _ocr_with_aliyun(image_url=image_url, image_base64=image_base64)
            ocr_used = "阿里云 OCR"
            print("✅ 阿里云 OCR 识别成功")
        except Exception as e:
            print(f"❌ 阿里云 OCR 失败: {e}")
            raise
    elif ocr_provider == "llm":
        # 只使用 LLM（LLM 自带图形识别能力）
        print("🤖 使用 LLM Vision（文字+图形）...")
        raw_text = await _ocr_with_llm(llm, image_url=image_url, image_base64=image_base64)
        ocr_used = "LLM Vision"
        print("✅ LLM Vision 识别成功")
        use_vision_enhancement = False  # LLM 已经识别了图形，无需再次增强
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
                print("✅ LLM Vision 识别成功")
                use_vision_enhancement = False  # LLM 已经识别了图形
            except Exception as e2:
                print(f"❌ LLM Vision 也失败: {e2}")
                raise Exception(f"所有 OCR 提供者都失败。阿里云: {e}，LLM: {e2}")
    
    print(f"\n📝 OCR 文字识别结果（{ocr_used}）：")
    print("-"*80)
    print(raw_text)
    print("-"*80)
    print(f"文本长度: {len(raw_text)} 字符\n")

    # ========== 第二步：Vision 增强（识别几何图形）==========
    # 只有使用阿里云 OCR 时才需要额外用 Vision 识别图形
    if use_vision_enhancement and ocr_used.startswith("阿里云"):
        raw_text = await _enhance_with_vision(llm, raw_text, image_url, image_base64)

    # ========== 第三步：题目结构化解析 ==========
    print("\n🔧 正在解析题目结构...")
    parser_prompt = _load_parser_prompt()
    parser_result = await llm.chat_json(
        system_prompt=parser_prompt,
        user_message=raw_text,
        model=None,  # 使用默认模型
    )

    problems: List[ParsedProblem] = []

    if isinstance(parser_result, dict) and "problems" in parser_result:
        for item in parser_result["problems"]:
            try:
                problems.append(ParsedProblem(**item))
            except Exception as e:
                print(f"⚠️  解析题目时出错: {e}")
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
