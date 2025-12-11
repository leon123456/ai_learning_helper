# app/schemas/paper.py

"""
试卷结构化识别相关的数据模型
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.diagnose import Problem, DiagnoseResult


# =========================
#  阿里云试卷识别返回的原始结构
# =========================

class Position(BaseModel):
    """坐标点"""
    x: int
    y: int


class QuestionPosition(BaseModel):
    """题目位置信息（用于前端高亮）"""
    pos_list: List[List[Position]]


class QuestionElement(BaseModel):
    """题目元素（题干、选项等）"""
    type: int  # 0=题干，1=选项，2=答案区域
    text: str
    pos_list: List[List[Position]]


class StructuredQuestion(BaseModel):
    """阿里云识别的结构化题目"""
    index: int  # 题号
    type: int   # 0=选择题，1=填空题，2=主观题
    text: str   # 完整题目文本
    pos_list: List[List[Position]]  # 题目坐标
    element_list: List[QuestionElement]  # 题目元素列表


class PaperSection(BaseModel):
    """试卷大题分区（如选择题、填空题等）"""
    part_title: str  # 大题标题，如"选择题"、"填空题"
    pos_list: Optional[List[List[Position]]] = None  # 大题标题位置
    subject_list: List[StructuredQuestion]  # 该大题下的小题列表


class PaperFigure(BaseModel):
    """试卷中的图形/配图
    
    阿里云返回的图形信息，包含位置和类型
    前端可根据坐标从原图中截取配图
    """
    type: str  # 图形类型：subject_pattern（题目配图）、table（表格）等
    x: int     # 左上角 X 坐标
    y: int     # 左上角 Y 坐标
    w: int     # 宽度
    h: int     # 高度
    points: Optional[List[Position]] = None  # 四角坐标（更精确）
    
    def to_crop_info(self) -> Dict[str, int]:
        """返回裁剪信息，用于从原图截取配图"""
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}
    
    def to_description(self) -> str:
        """返回配图描述，用于传递给 LLM"""
        type_names = {
            "subject_pattern": "题目配图",
            "subject_bracket": "括号/符号",
            "table": "表格",
        }
        type_name = type_names.get(self.type, self.type)
        return f"[{type_name}，位置:({self.x},{self.y})，尺寸:{self.w}x{self.h}]"


class PaperStructure(BaseModel):
    """试卷结构化识别结果"""
    page_id: int
    page_title: str
    width: int
    height: int
    part_info: List[PaperSection]  # 大题分区列表
    figure: Optional[List[PaperFigure]] = []  # 图形列表
    raw_data: Optional[Dict[str, Any]] = None  # 保留原始数据


# =========================
#  API 请求和响应结构
# =========================

class PaperOCRRequest(BaseModel):
    """试卷OCR识别请求"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None


class ParsedQuestion(BaseModel):
    """解析后的标准化题目
    
    包含从阿里云返回数据转换后的标准题目格式
    """
    index: int  # 题号
    type: str   # choice | fill | solve | proof | short_answer
    question: str  # 题干
    options: Optional[List[str]] = None  # 选项（仅选择题）
    position: List[List[Position]]  # 题目坐标（用于前端高亮）
    knowledge_points: List[str] = []  # 知识点（初始为空，可后续推断）
    difficulty: str = "medium"  # 难度（初始为中等）
    
    # 额外信息
    section_title: Optional[str] = None  # 所属大题标题
    elements: Optional[List[QuestionElement]] = None  # 题目元素详情
    
    # 配图信息（用于传递给 LLM）
    figures: List[PaperFigure] = []  # 该题目关联的配图列表
    has_figure: bool = False  # 是否包含配图
    figure_description: Optional[str] = None  # 配图描述（用于纯文本传递给 LLM）
    
    # 原始图片信息（用于 Vision 模型）
    image_url: Optional[str] = None  # 原始试卷图片 URL
    image_base64: Optional[str] = None  # 原始试卷图片 base64（用于截取配图）


class PaperOCRResponse(BaseModel):
    """试卷OCR识别响应"""
    paper_structure: PaperStructure  # 原始结构化数据
    questions: List[ParsedQuestion]  # 解析后的标准题目列表
    total_questions: int  # 题目总数
    figures: List[PaperFigure] = []  # 所有配图（方便前端直接使用）


# =========================
#  试卷批量诊断相关
# =========================

class QuestionAnswer(BaseModel):
    """单个题目的答案
    
    用于批量诊断时，用户提交每道题的答案
    """
    question_index: int  # 题号（对应 ParsedQuestion.index）
    user_answer: str  # 用户答案


class BatchDiagnoseRequest(BaseModel):
    """批量诊断请求
    
    用户上传试卷图片后，先调用 OCR 识别得到题目列表，
    然后用户作答后，提交所有答案进行批量诊断
    """
    questions: List[ParsedQuestion]  # 题目列表（来自 OCR 识别结果）
    answers: List[QuestionAnswer]  # 用户答案列表


class QuestionDiagnoseResult(BaseModel):
    """单题诊断结果（带题号）
    
    在批量诊断中，需要知道每个诊断结果对应哪道题
    """
    question_index: int  # 题号
    question: ParsedQuestion  # 题目信息
    diagnose_result: DiagnoseResult  # 诊断结果


class BatchDiagnoseResponse(BaseModel):
    """批量诊断响应"""
    results: List[QuestionDiagnoseResult]  # 每道题的诊断结果
    summary: "DiagnoseSummary"  # 总体诊断摘要


class DiagnoseSummary(BaseModel):
    """诊断摘要
    
    对整张试卷的诊断结果进行汇总分析
    """
    total_questions: int  # 总题数
    answered_questions: int  # 已作答题数
    correct_count: int  # 正确题数
    wrong_count: int  # 错误题数
    unanswered_count: int  # 未作答题数
    accuracy: float  # 正确率（已作答题目中的正确率）
    average_mastery: float  # 平均掌握度
    
    # 按题型统计
    stats_by_type: Dict[str, "TypeStats"]  # 按题型的统计
    
    # 知识点薄弱项
    weak_knowledge_points: List["WeakKnowledgePoint"]
    
    # 总体建议
    overall_suggestion: str


class TypeStats(BaseModel):
    """按题型的统计"""
    total: int  # 该题型总数
    correct: int  # 正确数
    wrong: int  # 错误数
    unanswered: int  # 未作答数
    accuracy: float  # 正确率


class WeakKnowledgePoint(BaseModel):
    """薄弱知识点"""
    knowledge: str  # 知识点名称
    error_count: int  # 错误次数
    total_count: int  # 该知识点题目总数
    accuracy: float  # 正确率
    recommended_practice_count: int  # 建议练习题数

