// lib/paper-store.ts

/**
 * 试卷状态管理
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  PaperState,
  PaperOCRResponse,
  BatchDiagnoseResponse,
  PaperQuestion,
} from './paper-types';

interface PaperStore extends PaperState {
  // ========== 图片相关 ==========
  setPaperImage: (image: string | null, base64?: string | null) => void;
  setPaperImageBase64: (base64: string | null) => void;
  
  // ========== OCR 结果 ==========
  setOCRResult: (result: PaperOCRResponse | null) => void;
  
  // ========== 用户答案 ==========
  setUserAnswer: (questionIndex: number, answer: string) => void;
  setAllUserAnswers: (answers: Record<number, string>) => void;
  clearUserAnswers: () => void;
  
  // ========== 诊断结果 ==========
  setDiagnoseResult: (result: BatchDiagnoseResponse | null) => void;
  
  // ========== 当前题目 ==========
  setCurrentQuestionIndex: (index: number | null) => void;
  
  // ========== 加载状态 ==========
  setRecognizing: (loading: boolean) => void;
  setDiagnosing: (loading: boolean) => void;
  
  // ========== 错误处理 ==========
  setError: (error: string | null) => void;
  
  // ========== 重置 ==========
  reset: () => void;
  
  // ========== 辅助方法 ==========
  getQuestion: (index: number) => PaperQuestion | undefined;
  getAnsweredCount: () => number;
  getUnansweredCount: () => number;
}

const initialState: PaperState = {
  paperImage: null,
  paperImageBase64: null,
  ocrResult: null,
  userAnswers: {},
  diagnoseResult: null,
  currentQuestionIndex: null,
  isRecognizing: false,
  isDiagnosing: false,
  error: null,
};

export const usePaperStore = create<PaperStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // ========== 图片相关 ==========
      setPaperImage: (image, base64 = null) => set({
        paperImage: image,
        paperImageBase64: base64,
        // 清除之前的结果
        ocrResult: null,
        userAnswers: {},
        diagnoseResult: null,
        error: null,
      }),

      // ========== OCR 结果 ==========
      setOCRResult: (result) => set((state) => ({
        ocrResult: result,
        // 初始化用户答案为空
        userAnswers: result?.questions.reduce((acc, q) => {
          acc[q.index] = '';
          return acc;
        }, {} as Record<number, string>) || {},
      })),
      
      // 单独设置图片 base64（不清除其他数据）
      setPaperImageBase64: (base64: string | null) => set({ paperImageBase64: base64 }),

      // ========== 用户答案 ==========
      setUserAnswer: (questionIndex, answer) => set((state) => ({
        userAnswers: {
          ...state.userAnswers,
          [questionIndex]: answer,
        },
      })),

      setAllUserAnswers: (answers) => set({ userAnswers: answers }),

      clearUserAnswers: () => set((state) => ({
        userAnswers: state.ocrResult?.questions.reduce((acc, q) => {
          acc[q.index] = '';
          return acc;
        }, {} as Record<number, string>) || {},
      })),

      // ========== 诊断结果 ==========
      setDiagnoseResult: (result) => set({ diagnoseResult: result }),

      // ========== 当前题目 ==========
      setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),

      // ========== 加载状态 ==========
      setRecognizing: (loading) => set({ isRecognizing: loading }),
      setDiagnosing: (loading) => set({ isDiagnosing: loading }),

      // ========== 错误处理 ==========
      setError: (error) => set({ error }),

      // ========== 重置 ==========
      reset: () => set(initialState),

      // ========== 辅助方法 ==========
      getQuestion: (index) => {
        const state = get();
        return state.ocrResult?.questions.find(q => q.index === index);
      },

      getAnsweredCount: () => {
        const state = get();
        return Object.values(state.userAnswers).filter(a => a?.trim()).length;
      },

      getUnansweredCount: () => {
        const state = get();
        const total = state.ocrResult?.questions.length || 0;
        const answered = Object.values(state.userAnswers).filter(a => a?.trim()).length;
        return total - answered;
      },
    }),
    {
      name: 'paper-storage', // localStorage key
      partialize: (state) => ({
        // 只持久化部分状态
        paperImage: state.paperImage,
        ocrResult: state.ocrResult,
        userAnswers: state.userAnswers,
        diagnoseResult: state.diagnoseResult,
      }),
    }
  )
);

// ==================== 选择器 ====================

/**
 * 获取当前题目
 */
export function useCurrentQuestion() {
  const { ocrResult, currentQuestionIndex } = usePaperStore();
  if (!ocrResult || currentQuestionIndex === null) return null;
  return ocrResult.questions.find(q => q.index === currentQuestionIndex);
}

/**
 * 获取题目诊断结果
 */
export function useQuestionDiagnoseResult(questionIndex: number) {
  const { diagnoseResult } = usePaperStore();
  return diagnoseResult?.results.find(r => r.question_index === questionIndex);
}

/**
 * 获取答题进度
 */
export function useAnswerProgress() {
  const { ocrResult, userAnswers } = usePaperStore();
  const total = ocrResult?.questions.length || 0;
  const answered = Object.values(userAnswers).filter(a => a?.trim()).length;
  return {
    total,
    answered,
    unanswered: total - answered,
    progress: total > 0 ? (answered / total) * 100 : 0,
  };
}

