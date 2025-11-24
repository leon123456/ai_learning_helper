// lib/types.ts

// ==================== OCR 相关类型 ====================

export interface OCRRequest {
  image_url?: string;
  image_base64?: string;
}

export interface ParsedProblem {
  type: string; // "choice" | "fill_blank" | "short_answer" | "calculation"
  question: string;
  options?: string[]; // 对于选择题: ["A. xxx", "B. xxx", ...]
  knowledge_points: string[];
  difficulty: string; // "easy" | "medium" | "hard"
  correct_answer?: string; // OCR 可能识别到的答案
}

export interface OCRResponse {
  raw_text: string;
  problems: ParsedProblem[];
}

// ==================== 诊断相关类型 ====================

export interface Problem {
  type: string;
  question: string;
  options?: string[];
  knowledge_points: string[];
  difficulty: string;
  correct_answer?: string;
}

export interface DiagnoseRequest {
  problem: Problem;
  user_answer: string;
}

export interface RecommendedPractice {
  knowledge: string;
  difficulty: string;
  count: number;
}

export interface DiagnoseResult {
  correct: boolean;
  correct_answer: string;
  user_answer: string;
  error_type: string;
  analysis: string;
  mastery_score: number;
  next_action: string;
  recommended_practice: RecommendedPractice[];
  knowledge_gap?: string[];
}

// ==================== 练习生成相关类型 ====================

export interface GeneratePracticeRequest {
  knowledge_points: string[];
  difficulty: string;
  count: number;
  error_type?: string;
  context?: string;
}

export interface PracticeProblem {
  type: string;
  question: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
  knowledge_points: string[];
}

export interface GeneratePracticeResponse {
  practices: PracticeProblem[];
}

// ==================== 应用状态类型 ====================

export interface AppState {
  currentImage?: string | null;
  ocrResult?: OCRResponse | null;
  currentProblem?: ParsedProblem | null;
  userAnswer?: string;
  diagnoseResult?: DiagnoseResult | null;
  isLoading: boolean;
  error?: string | null;
}

// ==================== UI 组件类型 ====================

export type QuestionType = "choice" | "fill_blank" | "short_answer" | "calculation";

export interface UploadState {
  file: File | null;
  preview: string | null;
  isUploading: boolean;
  error: string | null;
}

