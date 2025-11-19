# app/services/diagnostic.py

import re
import math
from typing import Dict, Tuple, Optional
from app.schemas.diagnose import (
    Problem,
    DiagnoseRequest,
    DiagnoseResult,
    RecommendedPractice,
    CachedAnswer
)

import json

def ensure_json_dict(response):
    if isinstance(response, dict):
        return response

    if isinstance(response, str):
        s = response.strip()

        # 尝试直接解析
        try:
            return json.loads(s)
        except:
            pass

        # 尝试截取 {...}
        try:
            start = s.index("{")
            end = s.rindex("}") + 1
            cleaned = s[start:end]
            return json.loads(cleaned)
        except:
            pass

    raise ValueError(f"LLM 返回无法解析为 JSON: {response}")



# =========================
#  简易内存缓存（可升级为 Redis / DB）
# =========================
_ANSWER_CACHE: Dict[str, CachedAnswer] = {}


# =========================
#  工具函数：标准化字符串
# =========================
def normalize(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().lower())


# =========================
#  数值容差判断（默认 ±1%）
# =========================
def numeric_equal(a: str, b: str, tol: float = 0.01) -> bool:
    try:
        va = float(a)
        vb = float(b)
        if va == 0:
            return abs(vb) < 1e-6
        return abs(va - vb) / abs(va) <= tol
    except:
        return False


# =========================
#  rule-based 判断模块
#  用于题库内题目 + LLM 求解出的正确答案
# =========================
def rule_based_judge(problem: Problem, correct: str, user: str) -> bool:
    if problem.type == "choice":
        # 标准化选项
        return normalize(correct) == normalize(user)

    if problem.type == "fill":
        # 尝试数值判断
        if numeric_equal(correct, user):
            return True

        # 单位去除（如：2cm == 2 cm）
        correct_clean = re.sub(r"[a-zA-Z]", "", correct)
        user_clean = re.sub(r"[a-zA-Z]", "", user)
        if numeric_equal(correct_clean, user_clean):
            return True

        return normalize(correct) == normalize(user)

    # 主观题 → 不由规则判断
    return False


# =========================
#  诊断引擎主类
# =========================
class DiagnosticEngine:

    def __init__(self, llm):
        self.llm = llm  # LLMClient 实例

    # ===========================================
    #  模块 1：自动求解缺失的正确答案（LLM fallback）
    # ===========================================
    async def solve_correct_answer(self, problem: Problem) -> Tuple[str, str]:
        """
        返回 (correct_answer, llm_reason)
        """

        # 1. 优先读取缓存题库
        if problem.question in _ANSWER_CACHE:
            cached = _ANSWER_CACHE[problem.question]
            return cached.correct_answer, cached.llm_reason

        # 2. 调 LLM 求解正确答案
        system_prompt = """
你是一个智能求解机器人，你的任务是根据题目自动求出唯一正确答案。
如果是选择题，请返回选项字母（A/B/C/D）。
如果是填空题，请返回数值或表达式。
严格返回 JSON：
{
  "llm_answer": "...",
  "llm_reason": "..."
}
"""
        user_prompt = f"题目如下：\n\n{problem.question}\n选项：{problem.options}"

        raw = await self.llm.chat(
            system_prompt=system_prompt,
            user_message=user_prompt,
            model=None,
            response_format="json"
        )

        resp = ensure_json_dict(raw)

        llm_answer = resp.get("llm_answer")
        llm_reason = resp.get("llm_reason", "")

        # 3. 写入缓存题库
        _ANSWER_CACHE[problem.question] = CachedAnswer(
            question=problem.question,
            correct_answer=llm_answer,
            llm_reason=llm_reason,
            knowledge_points=problem.knowledge_points
        )

        return llm_answer, llm_reason

    # ===========================================
    #  模块 2：主观题诊断（LLM）
    # ===========================================
    async def llm_diagnose(self, problem: Problem, correct_answer: str, user_answer: str):
        system_prompt = open("app/prompt/diagnostic.md").read()

        user_prompt = {
            "problem": problem.model_dump(),
            "correct_answer": correct_answer,
            "user_answer": user_answer
        }

        raw = await self.llm.chat(
            system_prompt=system_prompt,
            user_message=str(user_prompt),
            model=None,
            response_format="json"
        )

        resp = ensure_json_dict(raw)
        return resp

    # ===========================================
    #  模块 3：完整诊断流程（混合模式）
    # ===========================================
    async def diagnose(self, req: DiagnoseRequest) -> DiagnoseResult:
        problem: Problem = req.problem
        user_answer: str = req.user_answer

        # 1. 获取正确答案（题库内 or LLM fallback）
        if problem.correct_answer:
            correct_answer = problem.correct_answer
            correct_reason = "来自题库"
        else:
            correct_answer, correct_reason = await self.solve_correct_answer(problem)

        # 2. rule-based 判断对错（仅限客观题）
        if problem.type in ["choice", "fill"]:
            is_correct = rule_based_judge(problem, correct_answer, user_answer)
        else:
            is_correct = False  # 主观题先交给 LLM

        # 3. 调 LLM 做完整诊断（包括题库内 + 题库外）
        llm_result = await self.llm_diagnose(problem, correct_answer, user_answer)

        # 4. 返回结构化 DiagnoseResult
        return DiagnoseResult(
            correct=is_correct,
            correct_answer=correct_answer,
            user_answer=user_answer,
            error_type=llm_result.get("error_type", "其他"),
            analysis=llm_result.get("analysis", ""),
            mastery_score=int(llm_result.get("mastery_score", 50)),
            next_action=llm_result.get("next_action", ""),
            recommended_practice=[
                RecommendedPractice(**item)
                for item in llm_result.get("recommended_practice", [])
            ]
        )
