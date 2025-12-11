// lib/paper-api.ts

/**
 * 试卷结构化识别 API
 */

import axios from 'axios';
import {
  PaperOCRRequest,
  PaperOCRResponse,
  BatchDiagnoseRequest,
  BatchDiagnoseResponse,
} from './paper-types';

// API 基础 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// 创建 axios 实例
const paperApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 180 秒超时（试卷识别可能较慢）
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
paperApiClient.interceptors.request.use(
  (config) => {
    console.log(`📡 试卷API请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ 请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
paperApiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ 试卷API响应成功: ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ 试卷API错误:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== API 函数 ====================

/**
 * 试卷结构化识别
 * 上传整张试卷图片，自动切题识别
 */
export async function recognizePaper(request: PaperOCRRequest): Promise<PaperOCRResponse> {
  try {
    const response = await paperApiClient.post<PaperOCRResponse>(
      '/api/v1/paper/recognize',
      request
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail;
      throw new Error(detail || '试卷识别失败，请检查图片或网络连接');
    }
    throw error;
  }
}

/**
 * 批量诊断
 * 对整张试卷的所有题目进行诊断
 */
export async function batchDiagnose(request: BatchDiagnoseRequest): Promise<BatchDiagnoseResponse> {
  try {
    const response = await paperApiClient.post<BatchDiagnoseResponse>(
      '/api/v1/paper/batch-diagnose',
      request
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail;
      throw new Error(detail || '批量诊断失败，请稍后重试');
    }
    throw error;
  }
}

// ==================== 辅助函数 ====================

/**
 * 将文件转换为 Base64（不含 data:image 前缀）
 */
export async function fileToBase64Raw(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        // 移除 data:image/xxx;base64, 前缀
        const base64 = reader.result.split(',')[1] || reader.result;
        resolve(base64);
      } else {
        reject(new Error('文件读取失败'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * 将文件转换为 Base64（含 data:image 前缀，用于预览）
 */
export async function fileToBase64WithPrefix(file: File): Promise<string> {
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
 * 根据坐标裁剪图片（用于显示题目区域）
 */
export function cropImageByPosition(
  imageUrl: string,
  position: { x: number; y: number; w: number; h: number },
  padding: number = 10
): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas context not available'));
        return;
      }

      // 添加 padding
      const x = Math.max(0, position.x - padding);
      const y = Math.max(0, position.y - padding);
      const w = Math.min(img.width - x, position.w + padding * 2);
      const h = Math.min(img.height - y, position.h + padding * 2);

      canvas.width = w;
      canvas.height = h;
      ctx.drawImage(img, x, y, w, h, 0, 0, w, h);

      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = () => reject(new Error('Image load failed'));
    img.src = imageUrl;
  });
}

/**
 * 验证试卷图片
 */
export function validatePaperImage(file: File): void {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!validTypes.includes(file.type)) {
    throw new Error('请上传 JPG、PNG 或 WebP 格式的图片');
  }

  if (file.size > maxSize) {
    throw new Error('图片大小不能超过 10MB');
  }
}

