// lib/paper-types.ts

/**
 * 试卷结构化识别相关类型定义
 */

// ==================== 坐标和位置 ====================

export interface Position {
  x: number;
  y: number;
}

export interface FigureInfo {
  type: string;  // subject_pattern | table | subject_bracket
  x: number;
  y: number;
  w: number;
  h: number;
  description?: string;
}

// ==================== 题目结构 ====================

export interface PaperQuestion {
  index: number;           // 题号
  type: string;            // choice | fill | solve | proof | short_answer
  question: string;        // 题干
  options?: string[];      // 选项（选择题）
  position: Position[][];  // 题目坐标（用于高亮）
  section_title?: string;  // 所属大题标题
  knowledge_points: string[];
  difficulty: string;
  
  // 配图信息
  figures: FigureInfo[];
  has_figure: boolean;
  figure_description?: string;
}

// ==================== 试卷结构 ====================

export interface PaperSection {
  part_title: string;
  question_count: number;
}

export interface PaperStructure {
  page_id: number;
  page_title: string;
  width: number;
  height: number;
  sections: PaperSection[];
}

// ==================== API 请求/响应 ====================

export interface PaperOCRRequest {
  image_url?: string;
  image_base64?: string;
}

export interface PaperOCRResponse {
  paper_structure: PaperStructure;
  questions: PaperQuestion[];
  total_questions: number;
  figures: FigureInfo[];  // 所有配图
}

export interface QuestionAnswer {
  question_index: number;
  user_answer: string;
}

export interface BatchDiagnoseRequest {
  questions: PaperQuestion[];
  answers: QuestionAnswer[];
}

// ==================== 诊断结果 ====================

export interface SingleDiagnoseResult {
  correct: boolean;
  correct_answer: string;
  user_answer: string;
  error_type: string;
  analysis: string;
  mastery_score: number;
  next_action: string;
  recommended_practice: {
    knowledge: string;
    difficulty: string;
    count: number;
  }[];
}

export interface QuestionDiagnoseResult {
  question_index: number;
  question: PaperQuestion;
  diagnose_result: SingleDiagnoseResult;
}

export interface TypeStats {
  total: number;
  correct: number;
  wrong: number;
  unanswered: number;
  accuracy: number;
}

export interface WeakKnowledgePoint {
  knowledge: string;
  error_count: number;
  total_count: number;
  accuracy: number;
  recommended_practice_count: number;
}

export interface DiagnoseSummary {
  total_questions: number;
  answered_questions: number;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  accuracy: number;
  average_mastery: number;
  stats_by_type: Record<string, TypeStats>;
  weak_knowledge_points: WeakKnowledgePoint[];
  overall_suggestion: string;
}

export interface BatchDiagnoseResponse {
  results: QuestionDiagnoseResult[];
  summary: DiagnoseSummary;
}

// ==================== 前端状态 ====================

export interface PaperState {
  // 当前试卷图片
  paperImage: string | null;
  paperImageBase64: string | null;
  
  // OCR 识别结果
  ocrResult: PaperOCRResponse | null;
  
  // 用户答案
  userAnswers: Record<number, string>;  // { 题号: 答案 }
  
  // 诊断结果
  diagnoseResult: BatchDiagnoseResponse | null;
  
  // 当前查看的题目
  currentQuestionIndex: number | null;
  
  // 加载状态
  isRecognizing: boolean;
  isDiagnosing: boolean;
  
  // 错误信息
  error: string | null;
}

// ==================== 辅助类型 ====================

export type QuestionStatus = 'unanswered' | 'answered' | 'correct' | 'wrong';

export function getQuestionStatus(
  questionIndex: number,
  userAnswers: Record<number, string>,
  diagnoseResult: BatchDiagnoseResponse | null
): QuestionStatus {
  const answer = userAnswers[questionIndex];
  
  if (!diagnoseResult) {
    return answer?.trim() ? 'answered' : 'unanswered';
  }
  
  const result = diagnoseResult.results.find(r => r.question_index === questionIndex);
  if (!result) {
    return 'unanswered';
  }
  
  if (result.diagnose_result.error_type === '未作答') {
    return 'unanswered';
  }
  
  return result.diagnose_result.correct ? 'correct' : 'wrong';
}

export function getQuestionTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    choice: '选择题',
    fill: '填空题',
    solve: '解答题',
    proof: '证明题',
    short_answer: '简答题',
  };
  return labels[type] || type;
}

export function getStatusColor(status: QuestionStatus): string {
  const colors: Record<QuestionStatus, string> = {
    unanswered: 'bg-gray-100 text-gray-600',
    answered: 'bg-blue-100 text-blue-600',
    correct: 'bg-green-100 text-green-600',
    wrong: 'bg-red-100 text-red-600',
  };
  return colors[status];
}

