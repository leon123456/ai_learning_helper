# app/services/paper_diagnostic.py

"""
试卷批量诊断服务

功能：
1. 整合阿里云试卷结构化识别
2. 将识别结果转换为标准题目格式
3. 批量调用单题诊断服务
4. 生成试卷整体诊断报告
"""

from typing import List, Dict, Any
from collections import defaultdict

from app.schemas.paper import (
    PaperStructure,
    PaperSection,
    ParsedQuestion,
    QuestionAnswer,
    QuestionDiagnoseResult,
    BatchDiagnoseResponse,
    DiagnoseSummary,
    TypeStats,
    WeakKnowledgePoint,
    Position,
)
from app.schemas.diagnose import Problem, DiagnoseRequest
from app.services.aliyun_paper_ocr import (
    recognize_paper_structure, 
    parse_question_from_aliyun,
    merge_question_with_options,
)
from app.services.aliyun_paper_cut import (
    recognize_paper_cut,
    convert_to_parsed_questions as convert_paper_cut_questions,
)
from app.services.diagnostic import DiagnosticEngine


class PaperDiagnosticService:
    """试卷诊断服务"""
    
    def __init__(self, llm):
        """
        初始化试卷诊断服务
        
        Args:
            llm: LLM客户端实例
        """
        self.llm = llm
        self.diagnostic_engine = DiagnosticEngine(llm)
    
    async def recognize_and_parse_paper(
        self,
        image_url: str = None,
        image_base64: str = None,
    ) -> tuple[PaperStructure, List[ParsedQuestion]]:
        """
        识别并解析试卷
        
        步骤：
        1. 调用阿里云 OCR 识别试卷结构
        2. 将识别结果转换为标准题目格式
        
        Args:
            image_url: 试卷图片 URL
            image_base64: 试卷图片 base64 编码
        
        Returns:
            (paper_structure, questions): 试卷结构和题目列表
        """
        print("\n" + "="*80)
        print("📄 试卷结构化识别开始...")
        print("="*80)
        
        # 调用阿里云 OCR 识别试卷结构
        raw_data = await recognize_paper_structure(
            image_url=image_url,
            image_base64=image_base64
        )
        
        # 构建 PaperStructure
        paper_structure = PaperStructure(
            page_id=raw_data.get("page_id", 0),
            page_title=raw_data.get("page_title", ""),
            width=raw_data.get("width", 0),
            height=raw_data.get("height", 0),
            part_info=[],
            figure=raw_data.get("figure", []),
            raw_data=raw_data
        )
        
        # 获取所有配图和页面信息
        all_figures = raw_data.get("figure", [])
        page_height = raw_data.get("height", 0)
        
        if all_figures:
            print(f"\n🖼️  识别到 {len(all_figures)} 个配图/图形")
        
        # 解析每个大题和小题（关联配图）
        # 第一步：解析所有题目
        parsed_questions_raw = []
        
        for part in raw_data.get("part_info", []):
            section_title = part.get("part_title", "")
            print(f"\n📋 解析大题: {section_title}")
            
            for subject in part.get("subject_list", []):
                # 使用工具函数转换为标准格式（传递配图列表）
                parsed = parse_question_from_aliyun(
                    subject,
                    all_figures=all_figures,
                    page_height=page_height
                )
                parsed["section_title"] = section_title
                parsed_questions_raw.append(parsed)
                print(f"   ✓ 题目 {parsed['index']}: {parsed['type']} - {parsed['question'][:50]}...")
        
        # 第二步：合并被错误分割的题目和选项
        print("\n🔧 检查并合并分割的题目...")
        parsed_questions_merged = merge_question_with_options(parsed_questions_raw)
        
        # 第三步：转换为 ParsedQuestion 对象
        questions: List[ParsedQuestion] = []
        for parsed in parsed_questions_merged:
            question = ParsedQuestion(
                index=parsed["index"],
                type=parsed["type"],
                question=parsed["question"],
                options=parsed["options"],
                position=parsed["position"],
                section_title=parsed.get("section_title", ""),
                elements=parsed.get("elements"),
                figures=parsed.get("figures", []),
                has_figure=parsed.get("has_figure", False),
                figure_description=parsed.get("figure_description"),
                image_url=image_url,  # 保存原始图片 URL
                image_base64=image_base64,  # 保存原始图片 base64
            )
            questions.append(question)
            fig_info = f" (🖼️{len(question.figures)}图)" if question.has_figure else ""
            opt_info = f" ({len(question.options)}选项)" if question.options else ""
            print(f"   📝 最终题目 {question.index}: {question.type}{opt_info}{fig_info}")
        
        print(f"\n✅ 试卷解析完成，共识别到 {len(questions)} 道题目")
        print("="*80 + "\n")
        
        return paper_structure, questions
    
    async def recognize_and_parse_paper_cut(
        self,
        image_url: str = None,
        image_base64: str = None,
        cut_type: str = "question",
        image_type: str = "scan",
        subject: str = "Math",
    ) -> tuple[dict, List[ParsedQuestion]]:
        """
        使用 PaperCut API 识别并解析试卷
        
        与 recognize_and_parse_paper 功能相同，但使用不同的 API：
        - PaperCut: 词级别识别，公式识别更好，返回 page_list 结构
        - PaperStructed: 元素级别识别，大题分类更好，返回 part_info 结构
        
        Args:
            image_url: 试卷图片 URL
            image_base64: 试卷图片 base64 编码
            cut_type: 切题类型，question(切题) / answer(切答案)
            image_type: 图片类型，scan(扫描件) / photo(实拍图)
            subject: 学科类型，Math/Chinese/English 等
        
        Returns:
            (raw_data, questions): 原始数据和题目列表
        """
        print("\n" + "="*80)
        print("🔪 试卷切题识别开始 (PaperCut API)...")
        print("="*80)
        
        # 调用阿里云 PaperCut API
        raw_data = await recognize_paper_cut(
            image_url=image_url,
            image_base64=image_base64,
            cut_type=cut_type,
            image_type=image_type,
            subject=subject,
        )
        
        # 解析结果
        parsed_list = convert_paper_cut_questions(
            raw_data,
            image_url=image_url,
            image_base64=image_base64,
        )
        
        # 获取页面信息
        page_list = raw_data.get("page_list", [])
        page_width = page_list[0].get("width", 0) if page_list else 0
        page_height = page_list[0].get("height", 0) if page_list else 0
        
        # 转换为 ParsedQuestion 对象
        questions: List[ParsedQuestion] = []
        for parsed in parsed_list:
            question = ParsedQuestion(
                index=parsed["index"],
                type=parsed["type"],
                question=parsed["question"],
                options=parsed["options"],
                position=parsed["position"],
                section_title=parsed.get("section_title", ""),
                elements=parsed.get("elements"),
                figures=parsed.get("figures", []),
                has_figure=parsed.get("has_figure", False),
                figure_description=parsed.get("figure_description"),
                image_url=image_url,
                image_base64=image_base64,
            )
            questions.append(question)
            
            # 打印题目信息
            opt_info = f" ({len(question.options)}选项)" if question.options else ""
            formula_info = " 📐公式" if parsed.get("has_formula") else ""
            print(f"   📝 题目 {question.index}: {question.type}{opt_info}{formula_info}")
        
        print(f"\n✅ 试卷解析完成，共识别到 {len(questions)} 道题目")
        print("="*80 + "\n")
        
        return raw_data, questions
    
    async def batch_diagnose(
        self,
        questions: List[ParsedQuestion],
        answers: List[QuestionAnswer],
    ) -> BatchDiagnoseResponse:
        """
        批量诊断试卷
        
        Args:
            questions: 题目列表（来自 OCR 识别）
            answers: 用户答案列表
        
        Returns:
            批量诊断结果，包含每道题的诊断和整体摘要
        """
        print("\n" + "="*80)
        print("🔍 试卷批量诊断开始...")
        print(f"   - 题目总数: {len(questions)}")
        print(f"   - 用户答案数: {len(answers)}")
        print("="*80)
        
        # 构建答案字典，便于查找
        answer_dict: Dict[int, str] = {
            ans.question_index: ans.user_answer 
            for ans in answers
        }
        
        # 逐题诊断
        results: List[QuestionDiagnoseResult] = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] 诊断题目 {question.index}...")
            
            # 获取用户答案（如果没有则视为未作答）
            user_answer = answer_dict.get(question.index, "")
            
            # 转换配图格式
            from app.schemas.diagnose import ProblemFigure
            problem_figures = []
            for fig in question.figures:
                if isinstance(fig, dict):
                    problem_figures.append(ProblemFigure(
                        type=fig.get("type", "unknown"),
                        x=fig.get("x", 0),
                        y=fig.get("y", 0),
                        w=fig.get("w", 0),
                        h=fig.get("h", 0),
                    ))
            
            # 构建 Problem 对象（包含配图信息）
            problem = Problem(
                type=question.type,
                question=question.question,
                options=question.options,
                knowledge_points=question.knowledge_points,
                difficulty=question.difficulty,
                correct_answer=None,  # 由诊断引擎自动求解
                figures=problem_figures,
                has_figure=question.has_figure,
                figure_description=question.figure_description,
            )
            
            # 构建诊断请求（包含图片信息，用于 Vision 模型）
            diagnose_req = DiagnoseRequest(
                problem=problem,
                user_answer=user_answer,
                image_url=question.image_url,
                image_base64=question.image_base64,
            )
            
            # 调用单题诊断
            try:
                diagnose_result = await self.diagnostic_engine.diagnose(diagnose_req)
                
                # 记录结果
                results.append(QuestionDiagnoseResult(
                    question_index=question.index,
                    question=question,
                    diagnose_result=diagnose_result
                ))
                
                # 打印简要结果
                status = "✅ 正确" if diagnose_result.correct else "❌ 错误"
                if not user_answer or user_answer.strip() == "":
                    status = "⚪ 未作答"
                print(f"   {status} | 掌握度: {diagnose_result.mastery_score}%")
                
            except Exception as e:
                print(f"   ⚠️  诊断失败: {e}")
                # 跳过失败的题目，继续诊断下一题
                continue
        
        print(f"\n✅ 批量诊断完成，共诊断 {len(results)} 道题目")
        print("="*80 + "\n")
        
        # 生成诊断摘要
        summary = self._generate_summary(results)
        
        return BatchDiagnoseResponse(
            results=results,
            summary=summary
        )
    
    def _generate_summary(
        self,
        results: List[QuestionDiagnoseResult]
    ) -> DiagnoseSummary:
        """
        生成诊断摘要
        
        Args:
            results: 每道题的诊断结果
        
        Returns:
            诊断摘要
        """
        total = len(results)
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        total_mastery = 0
        
        # 按题型统计
        type_stats_data: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "correct": 0, "wrong": 0, "unanswered": 0}
        )
        
        # 知识点统计
        knowledge_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"error": 0, "total": 0}
        )
        
        for result in results:
            q_type = result.question.type
            diagnose = result.diagnose_result
            
            # 判断作答状态
            is_unanswered = diagnose.error_type == "未作答"
            
            if is_unanswered:
                unanswered_count += 1
                type_stats_data[q_type]["unanswered"] += 1
            elif diagnose.correct:
                correct_count += 1
                type_stats_data[q_type]["correct"] += 1
            else:
                wrong_count += 1
                type_stats_data[q_type]["wrong"] += 1
            
            type_stats_data[q_type]["total"] += 1
            total_mastery += diagnose.mastery_score
            
            # 统计知识点（仅错题和未作答）
            if not diagnose.correct or is_unanswered:
                for kp in result.question.knowledge_points:
                    knowledge_stats[kp]["error"] += 1
                    knowledge_stats[kp]["total"] += 1
            else:
                for kp in result.question.knowledge_points:
                    knowledge_stats[kp]["total"] += 1
        
        # 计算整体指标
        answered_questions = total - unanswered_count
        accuracy = (correct_count / answered_questions * 100) if answered_questions > 0 else 0
        average_mastery = total_mastery / total if total > 0 else 0
        
        # 构建按题型统计
        stats_by_type: Dict[str, TypeStats] = {}
        for q_type, stats in type_stats_data.items():
            answered = stats["total"] - stats["unanswered"]
            type_accuracy = (stats["correct"] / answered * 100) if answered > 0 else 0
            
            stats_by_type[q_type] = TypeStats(
                total=stats["total"],
                correct=stats["correct"],
                wrong=stats["wrong"],
                unanswered=stats["unanswered"],
                accuracy=type_accuracy
            )
        
        # 找出薄弱知识点（错误率高的）
        weak_kps: List[WeakKnowledgePoint] = []
        for kp, stats in knowledge_stats.items():
            if stats["total"] > 0:
                kp_accuracy = (1 - stats["error"] / stats["total"]) * 100
                if kp_accuracy < 80:  # 正确率低于80%视为薄弱
                    weak_kps.append(WeakKnowledgePoint(
                        knowledge=kp,
                        error_count=stats["error"],
                        total_count=stats["total"],
                        accuracy=kp_accuracy,
                        recommended_practice_count=max(3, stats["error"] * 2)  # 建议练习错题数的2倍
                    ))
        
        # 按错误率排序（错误率高的在前）
        weak_kps.sort(key=lambda x: x.accuracy)
        
        # 生成总体建议
        overall_suggestion = self._generate_overall_suggestion(
            total=total,
            answered=answered_questions,
            accuracy=accuracy,
            average_mastery=average_mastery,
            weak_kps=weak_kps
        )
        
        return DiagnoseSummary(
            total_questions=total,
            answered_questions=answered_questions,
            correct_count=correct_count,
            wrong_count=wrong_count,
            unanswered_count=unanswered_count,
            accuracy=accuracy,
            average_mastery=average_mastery,
            stats_by_type=stats_by_type,
            weak_knowledge_points=weak_kps[:5],  # 只返回前5个最薄弱的
            overall_suggestion=overall_suggestion
        )
    
    def _generate_overall_suggestion(
        self,
        total: int,
        answered: int,
        accuracy: float,
        average_mastery: float,
        weak_kps: List[WeakKnowledgePoint]
    ) -> str:
        """
        生成总体建议
        
        根据诊断结果生成针对性的学习建议
        """
        suggestions = []
        
        # 完成度建议
        if answered < total:
            unanswered = total - answered
            suggestions.append(
                f"有 {unanswered} 道题目未作答，建议完成所有题目以获得更全面的诊断。"
            )
        
        # 正确率建议
        if accuracy >= 90:
            suggestions.append("正确率优秀！继续保持，可以尝试更高难度的题目。")
        elif accuracy >= 70:
            suggestions.append("正确率良好，还有提升空间。建议重点复习错题涉及的知识点。")
        elif accuracy >= 50:
            suggestions.append("正确率中等，需要加强基础知识的学习和练习。")
        else:
            suggestions.append("正确率较低，建议系统性地复习相关知识点，并加强基础练习。")
        
        # 掌握度建议
        if average_mastery < 50:
            suggestions.append("整体掌握度偏低，建议从基础概念开始系统学习。")
        elif average_mastery < 70:
            suggestions.append("整体掌握度一般，需要针对性地加强薄弱环节。")
        
        # 薄弱知识点建议
        if weak_kps:
            top_weak = weak_kps[:3]
            kp_names = "、".join([kp.knowledge for kp in top_weak])
            suggestions.append(f"主要薄弱知识点：{kp_names}。建议集中练习这些知识点。")
        
        return " ".join(suggestions) if suggestions else "整体表现良好，继续加油！"

