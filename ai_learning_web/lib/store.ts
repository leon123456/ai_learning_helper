// lib/store.ts

import { create } from 'zustand';
import { AppState, OCRResponse, ParsedProblem, DiagnoseResult } from './types';

interface AppStore extends AppState {
  // 设置当前图片
  setCurrentImage: (image: string | null) => void;
  
  // 设置 OCR 结果
  setOCRResult: (result: OCRResponse | null) => void;
  
  // 设置当前题目
  setCurrentProblem: (problem: ParsedProblem | null) => void;
  
  // 设置用户答案
  setUserAnswer: (answer: string) => void;
  
  // 设置诊断结果
  setDiagnoseResult: (result: DiagnoseResult | null) => void;
  
  // 设置加载状态
  setLoading: (loading: boolean) => void;
  
  // 设置错误信息
  setError: (error: string | null) => void;
  
  // 重置所有状态
  reset: () => void;
}

const initialState: AppState = {
  currentImage: null,
  ocrResult: null,
  currentProblem: null,
  userAnswer: '',
  diagnoseResult: null,
  isLoading: false,
  error: null,
};

export const useAppStore = create<AppStore>((set) => ({
  ...initialState,
  
  setCurrentImage: (image) => set({ currentImage: image }),
  
  setOCRResult: (result) => set({ ocrResult: result }),
  
  setCurrentProblem: (problem) => set({ currentProblem: problem }),
  
  setUserAnswer: (answer) => set({ userAnswer: answer }),
  
  setDiagnoseResult: (result) => set({ diagnoseResult: result }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  reset: () => set(initialState),
}));

