# app/services/aliyun_paper_ocr.py

"""
阿里云试卷结构化识别 OCR 服务
API: RecognizeEduPaperStructed（精细版结构化切题）
参考文档: https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeedupaperstructed
基于官方示例: app/demo/alibaba_EduPaperStructed/alibabacloud_sample/sample.py

功能特点：
- 自动切题（题号识别准确）
- 自动结构化题干、选项、公式
- 返回题目坐标（可前端高亮）
- 适用整页、拍照、教辅、练习册
- 支持数学公式 OCR
- 支持题目内部图片坐标抽取
"""

import json
from typing import Optional, List, Dict, Any
from app.core.config import settings


class AliyunPaperOCRClient:
    """阿里云试卷结构化识别客户端"""
    
    def __init__(self):
        """
        初始化阿里云 OCR 客户端
        
        凭据配置优先级：
        1. .env 中的 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET（直接配置）
        2. 环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET
        3. 配置文件 ~/.alibabacloud/credentials
        """
        self.endpoint = settings.ALIYUN_OCR_ENDPOINT
        self.use_credential_client = False
        
        # 优先使用 .env 中的配置（更可靠）
        self.access_key_id = settings.ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = settings.ALIYUN_ACCESS_KEY_SECRET
        
        if self.access_key_id and self.access_key_secret:
            # 使用直接配置
            print(f"✅ 使用 .env 中配置的阿里云 AccessKey（ID: {self.access_key_id[:8]}...）")
        else:
            # 尝试使用 CredentialClient（从环境变量或配置文件读取）
            try:
                from alibabacloud_credentials.client import Client as CredentialClient
                self.credential_client = CredentialClient()
                self.use_credential_client = True
                print("✅ 使用阿里云 CredentialClient（从环境变量或配置文件读取）")
            except Exception as e:
                raise ValueError(
                    "阿里云 OCR 配置不完整。请选择以下方式之一：\n"
                    "【推荐】在 .env 文件中设置：\n"
                    "  ALIYUN_ACCESS_KEY_ID=你的AccessKeyId\n"
                    "  ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret\n"
                    "\n"
                    "或设置环境变量：\n"
                    "  export ALIBABA_CLOUD_ACCESS_KEY_ID='你的AccessKeyId'\n"
                    "  export ALIBABA_CLOUD_ACCESS_KEY_SECRET='你的AccessKeySecret'\n"
                    "\n"
                    "或创建配置文件 ~/.alibabacloud/credentials：\n"
                    "  [default]\n"
                    "  type = access_key\n"
                    "  access_key_id = 你的AccessKeyId\n"
                    "  access_key_secret = 你的AccessKeySecret\n"
                    f"\n原始错误: {e}"
                )
    
    async def recognize_paper_structure(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        识别试卷结构，自动切题并识别内容
        
        Args:
            image_url: 图片 URL（推荐使用，更稳定）
            image_base64: 图片 base64 编码（不含前缀）
        
        Returns:
            结构化的试卷数据，包含：
            {
                "page_id": 页码,
                "page_title": 页面标题,
                "width": 图片宽度,
                "height": 图片高度,
                "part_info": [  # 大题（如选择题、填空题等）
                    {
                        "part_title": "选择题",
                        "subject_list": [  # 小题列表
                            {
                                "index": 题号,
                                "type": 题型（0=选择题，1=填空题，2=主观题）,
                                "text": "题目完整文本",
                                "pos_list": [[{"x": x1, "y": y1}, ...]],  # 题目坐标
                                "element_list": [  # 题目元素（题干、选项等）
                                    {
                                        "type": 元素类型（0=题干，1=选项，2=答案区域）,
                                        "text": "元素文本",
                                        "pos_list": [[{"x": x1, "y": y1}, ...]],
                                        "content_list": [...]  # 更细粒度的内容
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "figure": [  # 图形坐标（题目中的图片、表格等）
                    {
                        "type": "图形类型",
                        "x": x坐标,
                        "y": y坐标,
                        "w": 宽度,
                        "h": 高度
                    }
                ]
            }
        """
        from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
        from alibabacloud_tea_util import models as util_models
        
        # 创建客户端配置
        if self.use_credential_client:
            # 使用 CredentialClient（推荐方式，从环境变量或配置文件读取）
            from alibabacloud_credentials.client import Client as CredentialClient
            credential = CredentialClient()
            config = open_api_models.Config(
                credential=credential
            )
        else:
            # 使用直接配置的 AccessKey（兼容方式）
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
            )
        
        # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
        if self.endpoint.startswith('ocr-api.'):
            config.endpoint = self.endpoint
        else:
            config.endpoint = f'ocr-api.{self.endpoint}'
        
        client = OcrApi20210707Client(config)
        
        # 准备请求参数
        request = ocr_api_20210707_models.RecognizeEduPaperStructedRequest()
        
        if image_url:
            # 使用图片 URL（推荐方式）
            request.url = image_url
            print(f"  ✓ 使用 URL 方式: {image_url[:80]}...")
        elif image_base64:
            # 使用 base64 编码的图片
            # 如果包含前缀，去掉
            if image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",")[1]
            
            # 关键：body 字段需要的是图片的原始二进制数据
            import base64 as b64
            image_bytes = b64.b64decode(image_base64)
            request.body = image_bytes
            
            print(f"  ✓ 使用 body 方式")
            print(f"    - Base64 长度: {len(image_base64)} 字符")
            print(f"    - 二进制大小: {len(image_bytes)} 字节 ({len(image_bytes)/1024:.2f} KB)")
        else:
            raise ValueError("必须提供 image_url 或 image_base64")
        
        try:
            # 调用 API（异步），设置更长的超时和重试
            runtime = util_models.RuntimeOptions(
                read_timeout=180000,  # 读取超时 180 秒（单位：毫秒）
                connect_timeout=60000,  # 连接超时 60 秒
                autoretry=True,  # 启用自动重试
                max_attempts=3,  # 最多重试 3 次
            )
            response = await client.recognize_edu_paper_structed_with_options_async(request, runtime)
            
            # 解析响应
            if not response or not response.body:
                raise Exception("阿里云试卷结构化识别 API 返回空响应")
            
            # 解析返回的 JSON 字符串
            data_str = response.body.data
            if not data_str:
                raise Exception("阿里云试卷结构化识别 API 返回的 data 为空")
            
            data = json.loads(data_str)
            
            # 验证返回数据
            if not data.get("part_info"):
                print("⚠️  警告：未识别到任何题目大题分区")
            
            print(f"✅ 试卷结构识别成功")
            print(f"   - 页面尺寸: {data.get('width')}x{data.get('height')}")
            print(f"   - 大题数量: {len(data.get('part_info', []))}")
            
            total_questions = sum(
                len(part.get('subject_list', [])) 
                for part in data.get('part_info', [])
            )
            print(f"   - 题目总数: {total_questions}")
            
            return data
            
        except ImportError as e:
            # 模块导入错误，给出明确的安装提示
            raise ImportError(
                f"阿里云 OCR SDK 未安装。请运行以下命令安装：\n"
                f"pip install alibabacloud-ocr-api20210707 alibabacloud-tea-openapi "
                f"alibabacloud-tea-util alibabacloud-credentials\n"
                f"原始错误: {e}"
            )
        except Exception as e:
            error_msg = str(e)
            # 如果是阿里云 SDK 的异常，提取更详细的错误信息
            if hasattr(e, 'message'):
                error_msg = e.message
            if hasattr(e, 'data') and e.data:
                recommend = e.data.get("Recommend", "")
                if recommend:
                    error_msg += f" 诊断地址: {recommend}"
            
            raise Exception(f"阿里云试卷结构化识别失败: {error_msg}")


async def recognize_paper_structure(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> Dict[str, Any]:
    """
    使用阿里云 OCR 识别试卷结构
    
    Args:
        image_url: 图片 URL
        image_base64: 图片 base64 编码
    
    Returns:
        结构化的试卷数据
    """
    client = AliyunPaperOCRClient()
    return await client.recognize_paper_structure(
        image_url=image_url, 
        image_base64=image_base64
    )


def find_figures_for_question(
    question_pos_list: List[Any],
    all_figures: List[Dict[str, Any]],
    page_height: int = 0,
) -> List[Dict[str, Any]]:
    """
    根据题目坐标找出属于该题目的配图
    
    判断逻辑：
    1. 配图在题目区域内
    2. 配图紧邻题目区域（在题目下方或右侧）
    
    Args:
        question_pos_list: 题目的坐标列表
        all_figures: 所有配图列表
        page_height: 页面高度（用于计算相对位置）
    
    Returns:
        属于该题目的配图列表
    """
    if not question_pos_list or not all_figures:
        return []
    
    # 获取题目的边界框
    try:
        # pos_list 格式: [[{x, y}, {x, y}, {x, y}, {x, y}], ...]
        all_x = []
        all_y = []
        for pos_group in question_pos_list:
            for pos in pos_group:
                if isinstance(pos, dict):
                    all_x.append(pos.get("x", 0))
                    all_y.append(pos.get("y", 0))
        
        if not all_x or not all_y:
            return []
        
        q_left = min(all_x)
        q_right = max(all_x)
        q_top = min(all_y)
        q_bottom = max(all_y)
        
        # 扩展题目区域，包含紧邻的配图（向下和向右扩展 50%）
        q_height = q_bottom - q_top
        q_width = q_right - q_left
        extended_bottom = q_bottom + q_height * 0.5
        extended_right = q_right + q_width * 0.3
        
    except Exception:
        return []
    
    # 查找属于该题目的配图
    matched_figures = []
    for fig in all_figures:
        fig_x = fig.get("x", 0)
        fig_y = fig.get("y", 0)
        fig_w = fig.get("w", 0)
        fig_h = fig.get("h", 0)
        
        fig_center_x = fig_x + fig_w / 2
        fig_center_y = fig_y + fig_h / 2
        
        # 判断配图是否在题目区域内或紧邻区域
        # 条件：配图中心在扩展后的题目区域内
        if (q_left <= fig_center_x <= extended_right and
            q_top <= fig_center_y <= extended_bottom):
            matched_figures.append(fig)
    
    return matched_figures


def parse_question_from_aliyun(
    subject_data: Dict[str, Any],
    all_figures: List[Dict[str, Any]] = None,
    page_height: int = 0,
) -> Dict[str, Any]:
    """
    将阿里云返回的题目数据转换为标准的 Problem 格式
    
    Args:
        subject_data: 阿里云返回的单个题目数据
        all_figures: 所有配图列表（用于关联配图）
        page_height: 页面高度
        
    Returns:
        标准化的题目数据，包含：
        {
            "type": 题型,
            "question": 题干,
            "options": 选项列表（如果有）,
            "position": 题目坐标,
            "elements": 题目元素列表,
            "figures": 关联的配图列表,
            "figure_description": 配图描述
        }
    
    题型映射（阿里云）：
    - type=0: 选择题 -> "choice"
    - type=1: 填空题 -> "fill"
    - type=2: 主观题 -> "short_answer" / "solve" / "proof"
    """
    # 获取题目类型
    aliyun_type = subject_data.get("type", 2)
    type_mapping = {
        0: "choice",      # 选择题
        1: "fill",        # 填空题
        2: "short_answer" # 主观题（默认为简答题）
    }
    question_type = type_mapping.get(aliyun_type, "short_answer")
    
    # 获取完整题目文本
    full_text = subject_data.get("text", "")
    
    # 提取题干和选项
    question_text = ""
    options = []
    
    element_list = subject_data.get("element_list", [])
    for element in element_list:
        elem_type = element.get("type", -1)
        elem_text = element.get("text", "")
        
        if elem_type == 0:
            # 题干
            question_text = elem_text
        elif elem_type == 1 and aliyun_type == 0:
            # 选项（仅对选择题有效）
            options.append(elem_text)
    
    # 如果没有提取到题干，使用完整文本
    if not question_text:
        question_text = full_text
    
    # 获取题目坐标
    position = subject_data.get("pos_list", [])
    
    # 智能判断题型（如果是主观题，进一步细分）
    if question_type == "short_answer":
        # 通过关键词判断是解答题还是证明题
        if any(keyword in question_text for keyword in ["证明", "求证", "试证"]):
            question_type = "proof"
        elif any(keyword in question_text for keyword in ["计算", "求", "解", "解答", "解释"]):
            question_type = "solve"
    
    # 查找关联的配图
    figures = []
    figure_description = None
    if all_figures:
        figures = find_figures_for_question(position, all_figures, page_height)
        if figures:
            # 生成配图描述（用于传递给 LLM）
            fig_descs = []
            for i, fig in enumerate(figures, 1):
                fig_type = fig.get("type", "unknown")
                type_names = {
                    "subject_pattern": "题目配图",
                    "subject_bracket": "括号/符号",
                    "table": "表格",
                }
                type_name = type_names.get(fig_type, fig_type)
                fig_descs.append(f"配图{i}: {type_name}（位置: x={fig.get('x')}, y={fig.get('y')}, 尺寸: {fig.get('w')}x{fig.get('h')}）")
            figure_description = "\n".join(fig_descs)
    
    return {
        "type": question_type,
        "question": question_text,
        "options": options if options else None,
        "position": position,
        "elements": element_list,
        "index": subject_data.get("index", 0),
        "figures": figures,
        "has_figure": len(figures) > 0,
        "figure_description": figure_description,
        "raw_data": subject_data  # 保留原始数据供调试
    }


def is_options_only(text: str) -> bool:
    """
    判断文本是否只包含选项（没有题干）
    
    选项特征：
    - 以 A. A、A． 等开头
    - 包含多个选项标记 (A B C D)
    """
    if not text:
        return False
    
    text = text.strip()
    
    # 检查是否以选项标记开头
    option_patterns = [
        "A.", "A、", "A．", "A．", "$$A",
        "A .", "A,",
    ]
    starts_with_option = any(text.startswith(p) for p in option_patterns)
    
    # 检查是否包含多个选项标记
    option_markers = ["A.", "B.", "C.", "D.", "A、", "B、", "C、", "D、", "$$A", "$$B", "$$C", "$$D"]
    option_count = sum(1 for marker in option_markers if marker in text)
    
    # 如果以选项开头且包含多个选项标记，则判定为只有选项
    return starts_with_option and option_count >= 2


def extract_options_from_text(text: str) -> List[str]:
    """
    从纯选项文本中提取选项列表
    
    Args:
        text: 包含选项的文本，如 "A.√2 B.2 C.√7 D.2√2"
    
    Returns:
        选项列表，如 ["A.√2", "B.2", "C.√7", "D.2√2"]
    """
    import re
    
    if not text:
        return []
    
    # 尝试用选项标记分割
    # 匹配模式：A. B. C. D. 或 A、B、C、D、或 $$A $$B $$C $$D
    pattern = r'([A-D][.、．,]|(?:\$\$)?[A-D]\s*[.、．]?)'
    
    parts = re.split(pattern, text)
    
    options = []
    current_option = ""
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # 检查是否是新选项的开始
        if re.match(r'^[A-D][.、．,]?$', part) or re.match(r'^\$\$[A-D]', part):
            if current_option:
                options.append(current_option.strip())
            current_option = part
        else:
            current_option += " " + part if current_option else part
    
    if current_option:
        options.append(current_option.strip())
    
    return options


def merge_question_with_options(
    questions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    合并被错误分割的题目和选项
    
    阿里云 OCR 有时会把一道题的题干和选项分成两个 subject，
    这个函数会检测并合并这种情况。
    
    判断逻辑：
    1. 当前 subject 只包含选项（没有题干）
    2. 前一个 subject 是选择题但没有选项
    
    Args:
        questions: 原始解析的题目列表
    
    Returns:
        合并后的题目列表
    """
    if not questions or len(questions) < 2:
        return questions
    
    merged = []
    i = 0
    
    while i < len(questions):
        current = questions[i]
        
        # 检查当前题目的 question 是否只包含选项
        if is_options_only(current.get("question", "")):
            # 这是一个只有选项的 subject
            
            # 检查是否有前一个题目可以合并
            if merged and merged[-1].get("type") == "choice":
                prev = merged[-1]
                
                # 如果前一个题目没有选项，则合并
                if not prev.get("options"):
                    # 从当前文本中提取选项
                    options = extract_options_from_text(current.get("question", ""))
                    if options:
                        prev["options"] = options
                        print(f"   ⚡ 合并题目 {prev.get('index')}: 补充 {len(options)} 个选项")
                        i += 1
                        continue
        
        # 检查当前题目是选择题但没有选项
        if current.get("type") == "choice" and not current.get("options"):
            # 看下一个 subject 是否是选项
            if i + 1 < len(questions):
                next_q = questions[i + 1]
                if is_options_only(next_q.get("question", "")):
                    # 从下一个 subject 提取选项
                    options = extract_options_from_text(next_q.get("question", ""))
                    if options:
                        current["options"] = options
                        print(f"   ⚡ 合并题目 {current.get('index')}: 从后续获取 {len(options)} 个选项")
                        merged.append(current)
                        i += 2  # 跳过下一个
                        continue
        
        merged.append(current)
        i += 1
    
    return merged

