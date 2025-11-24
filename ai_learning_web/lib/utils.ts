// lib/utils.ts

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * 合并 Tailwind CSS 类名
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 格式化时间
 */
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * 获取题型中文名称
 */
export function getQuestionTypeName(type: string): string {
  const typeMap: Record<string, string> = {
    choice: '选择题',
    fill_blank: '填空题',
    short_answer: '简答题',
    calculation: '计算题',
  };
  return typeMap[type] || '未知题型';
}

/**
 * 获取难度等级中文名称和颜色
 */
export function getDifficultyInfo(difficulty: string): {
  name: string;
  color: string;
  bgColor: string;
} {
  const difficultyMap: Record<string, { name: string; color: string; bgColor: string }> = {
    easy: { name: '简单', color: 'text-green-600', bgColor: 'bg-green-50' },
    medium: { name: '中等', color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
    hard: { name: '困难', color: 'text-red-600', bgColor: 'bg-red-50' },
  };
  return difficultyMap[difficulty] || { name: '未知', color: 'text-gray-600', bgColor: 'bg-gray-50' };
}

/**
 * 获取掌握度等级
 */
export function getMasteryLevel(score: number): {
  level: string;
  color: string;
  description: string;
} {
  if (score >= 90) {
    return {
      level: '优秀',
      color: 'text-green-600',
      description: '你已经完全掌握了这个知识点！',
    };
  } else if (score >= 75) {
    return {
      level: '良好',
      color: 'text-blue-600',
      description: '掌握得不错，继续保持！',
    };
  } else if (score >= 60) {
    return {
      level: '及格',
      color: 'text-yellow-600',
      description: '基本掌握，还需要多加练习。',
    };
  } else if (score >= 40) {
    return {
      level: '待提高',
      color: 'text-orange-600',
      description: '还有进步空间，加油！',
    };
  } else {
    return {
      level: '需要加强',
      color: 'text-red-600',
      description: '建议系统复习基础知识。',
    };
  }
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * 延迟函数（用于演示加载效果）
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

