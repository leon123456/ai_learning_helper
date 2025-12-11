# app/services/aliyun_paper_cut.py

"""
阿里云试卷切题识别 OCR 服务
API: RecognizeEduPaperCut（试卷切题识别）
参考文档: https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeedupapercut

功能特点：
- 自动切题（题号识别准确）
- 每个词单独识别，包含坐标和分类信息
- 支持数学公式 OCR（recClassify=51 表示公式，LaTeX 格式）
- 返回完整的题目文本（text 字段）
- 适用整页试卷、拍照图片

与 RecognizeEduPaperStructed 的区别：
- PaperCut: 返回 page_list 结构，按页面组织，词级别识别
- PaperStructed: 返回 part_info 结构，按大题分类，元素级别识别（题干、选项分开）
"""

import json
import re
from typing import Optional, List, Dict, Any
from app.core.config import settings


class AliyunPaperCutClient:
    """阿里云试卷切题识别客户端"""
    
    def __init__(self):
        """
        初始化阿里云 OCR 客户端
        
        凭据配置：
        - .env 中的 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET
        """
        self.endpoint = settings.ALIYUN_OCR_ENDPOINT
        self.access_key_id = settings.ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = settings.ALIYUN_ACCESS_KEY_SECRET
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError(
                "阿里云 OCR 配置不完整。请在 .env 文件中设置：\n"
                "  ALIYUN_ACCESS_KEY_ID=你的AccessKeyId\n"
                "  ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret\n"
            )
        
        print(f"✅ 使用阿里云 AccessKey（ID: {self.access_key_id[:8]}...）")
    
    async def recognize_paper_cut(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        cut_type: str = "question",
        image_type: str = "scan",
        subject: str = "Math",
    ) -> Dict[str, Any]:
        """
        识别试卷并切题
        
        Args:
            image_url: 图片 URL（公网可访问）
            image_base64: 图片 base64 编码（不含前缀）
            cut_type: 切题类型，question(切题) / answer(切答案)
            image_type: 图片类型，scan(扫描件) / photo(实拍图)
            subject: 学科类型，Math/Chinese/English/Physics 等
        
        Returns:
            原始 API 响应数据，包含 page_list 结构：
            {
                "page_list": [
                    {
                        "page_id": 页码,
                        "width": 图片宽度,
                        "height": 图片高度,
                        "subject_list": [
                            {
                                "ids": ["1"],  # 题号
                                "text": "完整题目文本",
                                "content_list_info": [...],  # 题目区域坐标
                                "prism_wordsInfo": [...]     # 词级别信息
                            }
                        ]
                    }
                ]
            }
        """
        from alibabacloud_ocr_api20210707.client import Client as OcrApiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
        from alibabacloud_tea_util import models as util_models
        
        # 创建客户端配置
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
        )
        
        # 设置 endpoint
        if self.endpoint.startswith('ocr-api.'):
            config.endpoint = self.endpoint
        else:
            config.endpoint = f'ocr-api.{self.endpoint}'
        
        client = OcrApiClient(config)
        
        # 准备请求参数
        request = ocr_api_20210707_models.RecognizeEduPaperCutRequest()
        
        if image_url:
            # 使用图片 URL
            request.url = image_url
            print(f"  ✓ 使用 URL 方式: {image_url[:80]}...")
        elif image_base64:
            # 使用 base64 编码的图片
            # 如果包含前缀，去掉
            if image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",")[1]
            
            # body 字段需要的是图片的原始二进制数据
            import base64 as b64
            image_bytes = b64.b64decode(image_base64)
            request.body = image_bytes
            
            print(f"  ✓ 使用 body 方式")
            print(f"    - 二进制大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
        else:
            raise ValueError("必须提供 image_url 或 image_base64")
        
        # 设置必需参数
        request.cut_type = cut_type      # question / answer
        request.image_type = image_type  # scan / photo（必需！）
        request.subject = subject        # 学科类型
        
        print(f"  ✓ cut_type: {cut_type}")
        print(f"  ✓ image_type: {image_type}")
        print(f"  ✓ subject: {subject}")
        
        try:
            # 调用 API（异步），设置更长的超时和重试
            runtime = util_models.RuntimeOptions(
                read_timeout=180000,   # 读取超时 180 秒
                connect_timeout=60000, # 连接超时 60 秒
                autoretry=True,        # 启用自动重试
                max_attempts=3,        # 最多重试 3 次
            )
            
            response = await client.recognize_edu_paper_cut_with_options_async(request, runtime)
            
            # 解析响应
            if not response or not response.body:
                raise Exception("阿里云试卷切题识别 API 返回空响应")
            
            # 解析返回的 JSON 字符串
            data_str = response.body.data
            if not data_str:
                raise Exception("阿里云试卷切题识别 API 返回的 data 为空")
            
            data = json.loads(data_str)
            
            # 统计信息
            page_count = len(data.get("page_list", []))
            total_questions = sum(
                len(page.get("subject_list", []))
                for page in data.get("page_list", [])
            )
            
            print(f"✅ 试卷切题识别成功")
            print(f"   - 页面数量: {page_count}")
            print(f"   - 题目总数: {total_questions}")
            
            return data
            
        except ImportError as e:
            raise ImportError(
                f"阿里云 OCR SDK 未安装。请运行以下命令安装：\n"
                f"pip install alibabacloud-ocr-api20210707 alibabacloud-tea-openapi "
                f"alibabacloud-tea-util alibabacloud-credentials\n"
                f"原始错误: {e}"
            )
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'message'):
                error_msg = e.message
            if hasattr(e, 'data') and e.data:
                recommend = e.data.get("Recommend", "")
                if recommend:
                    error_msg += f" 诊断地址: {recommend}"
            
            raise Exception(f"阿里云试卷切题识别失败: {error_msg}")


async def recognize_paper_cut(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
    cut_type: str = "question",
    image_type: str = "scan",
    subject: str = "Math",
) -> Dict[str, Any]:
    """
    使用阿里云 OCR 识别试卷并切题
    
    这是便捷函数，内部创建客户端并调用 API
    
    Args:
        image_url: 图片 URL
        image_base64: 图片 base64 编码
        cut_type: 切题类型，question(切题) / answer(切答案)
        image_type: 图片类型，scan(扫描件) / photo(实拍图)
        subject: 学科类型
    
    Returns:
        原始 API 响应数据
    """
    client = AliyunPaperCutClient()
    return await client.recognize_paper_cut(
        image_url=image_url,
        image_base64=image_base64,
        cut_type=cut_type,
        image_type=image_type,
        subject=subject,
    )


def parse_question_from_paper_cut(
    subject_data: Dict[str, Any],
    page_width: int = 0,
    page_height: int = 0,
) -> Dict[str, Any]:
    """
    将 PaperCut API 返回的单个题目数据转换为标准的 Problem 格式
    
    Args:
        subject_data: PaperCut 返回的单个题目数据
        page_width: 页面宽度
        page_height: 页面高度
        
    Returns:
        标准化的题目数据：
        {
            "index": 题号,
            "type": 题型（choice/fill/short_answer 等）,
            "question": 题干,
            "options": 选项列表,
            "position": 题目坐标,
            "text": 原始完整文本,
            "words_info": 词级别信息,
            "has_formula": 是否包含公式
        }
    
    示例输入:
        {
            "ids": ["1"],
            "text": "1.(1+5i)i的虚部为 A.-1 B.0 C.1 D.6",
            "prism_wordsInfo": [...]
        }
    
    示例输出:
        {
            "index": 1,
            "type": "choice",
            "question": "(1+5i)i的虚部为",
            "options": ["A.-1", "B.0", "C.1", "D.6"],
            ...
        }
    """
    # 获取题号
    ids = subject_data.get("ids", [])
    index = int(ids[0]) if ids else 0
    
    # 获取完整文本
    full_text = subject_data.get("text", "").strip()
    
    # 获取词级别信息
    words_info = subject_data.get("prism_wordsInfo", [])
    
    # 检查是否包含公式（recClassify=51 表示公式）
    has_formula = any(w.get("recClassify") == 51 for w in words_info)
    
    # 获取题目坐标
    content_list_info = subject_data.get("content_list_info", [])
    position = content_list_info[0].get("pos", []) if content_list_info else []
    
    # 解析题干和选项
    question_text, options, question_type = extract_question_and_options(full_text, words_info)
    
    return {
        "index": index,
        "type": question_type,
        "question": question_text,
        "options": options,
        "position": position,
        "text": full_text,
        "words_info": words_info,
        "has_formula": has_formula,
        "raw_data": subject_data,
    }


def extract_question_and_options(
    full_text: str,
    words_info: List[Dict[str, Any]] = None,
) -> tuple:
    """
    从完整文本中提取题干和选项
    
    Args:
        full_text: 完整的题目文本
        words_info: 词级别信息（用于更精确的分割）
    
    Returns:
        (question_text, options, question_type)
    
    示例:
        输入: "1.(1+5i)i的虚部为 A.-1 B.0 C.1 D.6"
        输出: ("(1+5i)i的虚部为", ["A.-1", "B.0", "C.1", "D.6"], "choice")
    
    关键逻辑：
        - 选项格式必须是 "A." 或 "A、" 后面跟内容
        - 公式中的字母（如 $$A$$）不是选项
        - 选项通常在题目末尾，按 A B C D 顺序出现
    """
    if not full_text:
        return "", [], "short_answer"
    
    # 去掉题号前缀（如 "1." "2." 等）
    text = re.sub(r'^\d+[.、．]\s*', '', full_text.strip())
    
    # 方法1: 使用 words_info 中的选项信息（更准确）
    if words_info:
        options_from_words = extract_options_from_words_info(words_info)
        if len(options_from_words) >= 2:
            # 找到第一个选项在原文中的位置
            first_option = options_from_words[0]
            # 查找选项在文本中的位置（考虑选项可能以 A. A、$$A. 开头）
            first_pos = find_option_position(text, first_option)
            if first_pos >= 0:
                question_text = text[:first_pos].strip()
                return question_text, options_from_words, "choice"
    
    # 方法2: 使用正则表达式匹配标准选项格式
    # 更严格的选项匹配：必须是独立的 A. B. C. D.（不在公式内）
    # 匹配模式：行首或空格后的 A. A、A．或 $$A . （公式格式的选项）
    option_pattern = r'(?:^|\s)(\$\$[A-D]\s*[.、．]|\s[A-D][.、．])'
    
    # 查找所有可能的选项起始位置
    matches = list(re.finditer(option_pattern, text))
    
    # 过滤：确保 A B C D 按顺序出现
    valid_options = []
    expected_letters = ['A', 'B', 'C', 'D']
    letter_idx = 0
    
    for match in matches:
        matched_text = match.group(1).strip()
        # 提取字母
        letter = re.search(r'[A-D]', matched_text)
        if letter:
            letter = letter.group()
            # 检查是否是期望的下一个字母
            if letter_idx < len(expected_letters) and letter == expected_letters[letter_idx]:
                valid_options.append(match)
                letter_idx += 1
    
    if len(valid_options) >= 2:
        # 这是选择题
        first_option_pos = valid_options[0].start()
        question_text = text[:first_option_pos].strip()
        
        # 提取选项内容
        options = []
        for i, match in enumerate(valid_options):
            start = match.start()
            end = valid_options[i + 1].start() if i + 1 < len(valid_options) else len(text)
            option_text = text[start:end].strip()
            if option_text:
                options.append(option_text)
        
        return question_text, options, "choice"
    
    # 方法3: 尝试更宽松的匹配（用于处理特殊格式）
    # 查找末尾的选项块（如 "A.轻风 B.微风 C.和风 D.劲风"）
    tail_options = extract_tail_options(text)
    if tail_options:
        # 找到选项块的起始位置
        first_opt = tail_options[0]
        pos = text.rfind(first_opt)
        if pos > 0:
            question_text = text[:pos].strip()
            return question_text, tail_options, "choice"
    
    # 检查是否是填空题（包含下划线或空格填空标记）
    if "___" in text or "____" in text or re.search(r'_{3,}', text):
        return text, [], "fill"
    
    # 检查是否是证明题
    if any(kw in text for kw in ["证明", "求证", "试证"]):
        return text, [], "proof"
    
    # 检查是否是解答题
    if any(kw in text for kw in ["计算", "求", "解", "解答"]):
        return text, [], "solve"
    
    # 默认为简答题
    return text, [], "short_answer"


def extract_options_from_words_info(words_info: List[Dict[str, Any]]) -> List[str]:
    """
    从词级别信息中提取选项
    
    通过 recClassify 和 word 内容判断哪些是选项
    
    Args:
        words_info: 词级别信息列表
    
    Returns:
        选项列表，如 ["A.-1", "B.0", "C.1", "D.6"]
    """
    options = []
    expected_letters = ['A', 'B', 'C', 'D']
    letter_idx = 0
    
    for word_info in words_info:
        word = word_info.get("word", "")
        
        # 检查是否是选项开头
        # 标准格式: A. A、A．或 $$A .（公式格式）
        if letter_idx < len(expected_letters):
            expected = expected_letters[letter_idx]
            
            # 检查各种选项格式
            is_option = False
            if word.startswith(f"{expected}.") or word.startswith(f"{expected}、"):
                is_option = True
            elif word.startswith(f"$${expected}") or word.startswith(f"$${ expected}"):
                is_option = True
            elif word.strip() == f"{expected}." or word.strip() == f"{expected}、":
                is_option = True
            
            if is_option:
                options.append(word.strip())
                letter_idx += 1
    
    return options


def find_option_position(text: str, option: str) -> int:
    """
    在文本中找到选项的位置
    
    Args:
        text: 完整文本
        option: 选项文本
    
    Returns:
        选项在文本中的位置，如果找不到返回 -1
    """
    # 直接查找
    pos = text.find(option)
    if pos >= 0:
        return pos
    
    # 尝试查找选项的开头部分（如 "A." "A、"）
    for pattern in [r'[A-D][.、．]', r'\$\$[A-D]']:
        match = re.search(pattern, option)
        if match:
            prefix = match.group()
            pos = text.find(prefix)
            if pos >= 0:
                return pos
    
    return -1


def extract_tail_options(text: str) -> List[str]:
    """
    从文本末尾提取选项（用于处理选项在最后的情况）
    
    Args:
        text: 完整文本
    
    Returns:
        选项列表
    """
    # 匹配末尾的选项块
    # 格式：A.xxx B.xxx C.xxx D.xxx
    pattern = r'([A-D][.、．][^\s]*(?:\s|$))'
    
    # 从后往前查找
    matches = list(re.finditer(pattern, text))
    
    if len(matches) >= 2:
        # 检查是否是连续的 A B C D
        options = []
        expected = ['A', 'B', 'C', 'D']
        
        for match in matches:
            opt_text = match.group(1).strip()
            letter = opt_text[0] if opt_text else ''
            
            if letter in expected:
                idx = expected.index(letter)
                # 确保按顺序
                if len(options) == idx:
                    options.append(opt_text)
        
        if len(options) >= 2:
            return options
    
    return []


def parse_paper_cut_response(
    response_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    解析 PaperCut API 的完整响应，转换为标准的试卷结构
    
    Args:
        response_data: PaperCut API 的原始响应
    
    Returns:
        标准化的试卷数据：
        {
            "page_count": 页面数量,
            "total_questions": 题目总数,
            "pages": [
                {
                    "page_id": 页码,
                    "width": 宽度,
                    "height": 高度,
                    "questions": [标准化的题目列表]
                }
            ]
        }
    """
    pages = []
    total_questions = 0
    
    for page_data in response_data.get("page_list", []):
        page_id = page_data.get("page_id", 0)
        width = page_data.get("width", 0)
        height = page_data.get("height", 0)
        
        questions = []
        for subject in page_data.get("subject_list", []):
            parsed = parse_question_from_paper_cut(subject, width, height)
            questions.append(parsed)
            total_questions += 1
        
        pages.append({
            "page_id": page_id,
            "width": width,
            "height": height,
            "questions": questions,
        })
    
    return {
        "page_count": len(pages),
        "total_questions": total_questions,
        "pages": pages,
    }


def convert_to_parsed_questions(
    response_data: Dict[str, Any],
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    将 PaperCut API 响应转换为 ParsedQuestion 兼容的格式
    
    这是主要的转换函数，用于将 PaperCut 的结果接入现有的诊断流程
    
    Args:
        response_data: PaperCut API 的原始响应
        image_url: 原始图片 URL（用于后续诊断）
        image_base64: 原始图片 base64（用于后续诊断）
    
    Returns:
        ParsedQuestion 兼容的题目列表
    """
    questions = []
    
    for page_data in response_data.get("page_list", []):
        page_width = page_data.get("width", 0)
        page_height = page_data.get("height", 0)
        
        for subject in page_data.get("subject_list", []):
            parsed = parse_question_from_paper_cut(subject, page_width, page_height)
            
            # 转换为 ParsedQuestion 兼容格式
            question = {
                "index": parsed["index"],
                "type": parsed["type"],
                "question": parsed["question"],
                "options": parsed["options"] if parsed["options"] else None,
                "position": parsed["position"],
                "section_title": "",  # PaperCut 不返回大题分类
                "elements": None,     # PaperCut 不返回元素列表
                "figures": [],        # 需要从 words_info 中提取
                "has_figure": False,  # 后续可以根据需要检测
                "figure_description": None,
                "knowledge_points": [],  # 由诊断引擎填充
                "difficulty": None,      # 由诊断引擎填充
                "image_url": image_url,
                "image_base64": image_base64,
                "raw_text": parsed["text"],
                "has_formula": parsed["has_formula"],
            }
            
            questions.append(question)
    
    return questions


async def recognize_and_parse_paper(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
    cut_type: str = "question",
    image_type: str = "scan",
    subject: str = "Math",
) -> tuple:
    """
    识别并解析试卷（高级接口）
    
    这是一个便捷函数，整合了 API 调用和结果解析
    
    Args:
        image_url: 图片 URL
        image_base64: 图片 base64 编码
        cut_type: 切题类型
        image_type: 图片类型
        subject: 学科类型
    
    Returns:
        (raw_data, parsed_questions): 原始数据和解析后的题目列表
    
    示例:
        raw_data, questions = await recognize_and_parse_paper(image_base64=img_b64)
        for q in questions:
            print(f"题目 {q['index']}: {q['type']} - {q['question'][:50]}...")
    """
    print("\n" + "=" * 80)
    print("🔪 试卷切题识别开始 (PaperCut)...")
    print("=" * 80)
    
    # 调用 API
    raw_data = await recognize_paper_cut(
        image_url=image_url,
        image_base64=image_base64,
        cut_type=cut_type,
        image_type=image_type,
        subject=subject,
    )
    
    # 解析结果
    questions = convert_to_parsed_questions(
        raw_data,
        image_url=image_url,
        image_base64=image_base64,
    )
    
    print(f"\n✅ 识别完成，共解析 {len(questions)} 道题目")
    for q in questions:
        opt_info = f" ({len(q['options'])}选项)" if q['options'] else ""
        formula_info = " 📐" if q.get('has_formula') else ""
        print(f"   [{q['index']}] {q['type']}{opt_info}{formula_info}: {q['question'][:40]}...")
    
    print("=" * 80 + "\n")
    
    return raw_data, questions
