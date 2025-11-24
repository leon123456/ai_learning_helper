// lib/api.ts

import axios, { AxiosError } from 'axios';
import {
  OCRRequest,
  OCRResponse,
  DiagnoseRequest,
  DiagnoseResult,
  GeneratePracticeRequest,
  GeneratePracticeResponse,
} from './types';

// API 基础 URL，从环境变量读取
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120 秒超时（OCR 可能较慢）
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器（可选：添加认证 token 等）
apiClient.interceptors.request.use(
  (config) => {
    console.log(`📡 API请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ 请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器（统一错误处理）
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API响应成功: ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API错误:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== API 函数 ====================

/**
 * 1. OCR 识别图片
 * @param request - 包含 image_url 或 image_base64
 * @returns OCR 解析结果
 */
export async function parseImage(request: OCRRequest): Promise<OCRResponse> {
  try {
    const response = await apiClient.post<OCRResponse>('/api/v1/ocr/parse', request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        'OCR 识别失败，请检查图片格式或网络连接'
      );
    }
    throw error;
  }
}

/**
 * 2. 学习诊断
 * @param request - 题目和用户答案
 * @returns 诊断结果
 */
export async function diagnoseProblem(request: DiagnoseRequest): Promise<DiagnoseResult> {
  try {
    const response = await apiClient.post<DiagnoseResult>('/api/v1/diagnose', request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        '诊断失败，请稍后重试'
      );
    }
    throw error;
  }
}

/**
 * 3. 生成推荐练习题（待后端实现）
 * @param request - 知识点、难度等参数
 * @returns 推荐练习题列表
 */
export async function generatePractice(
  request: GeneratePracticeRequest
): Promise<GeneratePracticeResponse> {
  try {
    const response = await apiClient.post<GeneratePracticeResponse>(
      '/api/v1/generate-practice',
      request
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || 
        '生成练习题失败，请稍后重试'
      );
    }
    throw error;
  }
}

/**
 * 4. 健康检查
 * @returns 服务器状态
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('无法连接到服务器，请检查后端服务是否启动');
  }
}

// ==================== 辅助函数 ====================

/**
 * 将文件转换为 Base64
 * @param file - 文件对象
 * @returns Base64 编码的字符串
 */
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error('文件读取失败'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * 验证图片格式
 * @param file - 文件对象
 * @returns 是否为有效图片
 */
export function isValidImage(file: File): boolean {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!validTypes.includes(file.type)) {
    throw new Error('请上传 JPG、PNG 或 WebP 格式的图片');
  }

  if (file.size > maxSize) {
    throw new Error('图片大小不能超过 10MB');
  }

  return true;
}

/**
 * 格式化错误消息
 * @param error - 错误对象
 * @returns 用户友好的错误消息
 */
export function formatErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return '发生未知错误，请稍后重试';
}

