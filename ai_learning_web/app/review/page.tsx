'use client'

/**
 * 单题回显和答案输入页面
 * 
 * 功能：
 * 1. 显示 OCR 识别出的题目
 * 2. 让用户输入/选择答案
 * 3. 提交诊断
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  Send,
  Image as ImageIcon,
  CheckCircle,
  Loader2,
  AlertCircle,
  Sparkles,
} from 'lucide-react'
import { useAppStore } from '@/lib/store'
import { diagnoseProblem, formatErrorMessage } from '@/lib/api'
import { Problem } from '@/lib/types'

export default function ReviewPage() {
  const router = useRouter()
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [textAnswer, setTextAnswer] = useState('')
  
  const {
    currentImage,
    currentProblem,
    setDiagnoseResult,
    setLoading,
    isLoading,
    setError,
    error,
  } = useAppStore()

  // 如果没有题目数据，跳转回上传页
  useEffect(() => {
    if (!currentProblem) {
      router.push('/upload')
    }
  }, [currentProblem, router])

  // 获取用户答案
  const getUserAnswer = (): string => {
    if (currentProblem?.type === 'choice') {
      return selectedOption || ''
    }
    return textAnswer.trim()
  }

  // 提交诊断
  const handleSubmit = async () => {
    if (!currentProblem) return

    const userAnswer = getUserAnswer()
    if (!userAnswer) {
      setError('请先输入或选择你的答案')
      return
    }

    try {
      setLoading(true)
      setError(null)

      // 构建 Problem 对象
      const problem: Problem = {
        type: currentProblem.type,
        question: currentProblem.question,
        options: currentProblem.options,
        knowledge_points: currentProblem.knowledge_points,
        difficulty: currentProblem.difficulty,
        correct_answer: currentProblem.correct_answer,
      }

      console.log('📤 开始诊断...')
      const result = await diagnoseProblem({
        problem,
        user_answer: userAnswer,
      })

      console.log('✅ 诊断成功:', result)
      setDiagnoseResult(result)

      // 跳转到结果页
      router.push('/result')

    } catch (err) {
      const errorMsg = formatErrorMessage(err)
      console.error('❌ 诊断失败:', errorMsg)
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  if (!currentProblem) {
    return null
  }

  const isChoice = currentProblem.type === 'choice'
  const hasAnswer = isChoice ? !!selectedOption : !!textAnswer.trim()

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* 顶部导航 */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => router.push('/upload')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>重新上传</span>
        </button>
        
        <h1 className="text-2xl font-bold text-gray-900">确认题目</h1>

        <div className="w-24" />
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* 左侧：原图预览 */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-gray-500" />
              原图预览
            </h2>
          </div>
          {currentImage && (
            <div className="p-4">
              <img
                src={currentImage}
                alt="试卷原图"
                className="w-full rounded-lg border border-gray-200"
              />
            </div>
          )}
        </div>

        {/* 右侧：题目内容和答案输入 */}
        <div className="space-y-6">
          {/* 题目卡片 */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-500" />
                  识别结果
                </h2>
                <span className="text-xs px-3 py-1 bg-white rounded-full text-indigo-600 font-medium border border-indigo-200">
                  {currentProblem.type === 'choice' ? '选择题' : 
                   currentProblem.type === 'fill_blank' ? '填空题' : 
                   currentProblem.type === 'calculation' ? '计算题' : '解答题'}
                </span>
              </div>
            </div>

            <div className="p-6">
              {/* 题干 */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">题目</h3>
                <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
                  {currentProblem.question}
                </p>
              </div>

              {/* 选项（选择题） */}
              {isChoice && currentProblem.options && currentProblem.options.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-3">选择你的答案</h3>
                  <div className="space-y-3">
                    {currentProblem.options.map((option, idx) => {
                      const optionLetter = option.charAt(0)
                      const isSelected = selectedOption === optionLetter
                      
                      return (
                        <button
                          key={idx}
                          onClick={() => setSelectedOption(optionLetter)}
                          className={`
                            w-full p-4 rounded-xl border-2 text-left transition-all duration-200
                            ${isSelected 
                              ? 'border-indigo-500 bg-indigo-50 shadow-md' 
                              : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'}
                          `}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`
                              w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all
                              ${isSelected 
                                ? 'border-indigo-500 bg-indigo-500' 
                                : 'border-gray-300'}
                            `}>
                              {isSelected && (
                                <CheckCircle className="w-4 h-4 text-white" />
                              )}
                            </div>
                            <span className={`text-base ${isSelected ? 'text-indigo-700 font-medium' : 'text-gray-700'}`}>
                              {option}
                            </span>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* 答案输入框（非选择题） */}
              {!isChoice && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">输入你的答案</h3>
                  <textarea
                    value={textAnswer}
                    onChange={(e) => setTextAnswer(e.target.value)}
                    placeholder="请输入你的答案..."
                    className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none transition-all"
                    rows={4}
                  />
                </div>
              )}

              {/* 知识点标签 */}
              {currentProblem.knowledge_points && currentProblem.knowledge_points.length > 0 && (
                <div className="pt-4 border-t border-gray-100">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">涉及知识点</h3>
                  <div className="flex flex-wrap gap-2">
                    {currentProblem.knowledge_points.map((point, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 text-sm rounded-full border border-blue-200"
                      >
                        {point}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-800">提交失败</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* 提交按钮 */}
          <button
            onClick={handleSubmit}
            disabled={isLoading || !hasAnswer}
            className={`
              w-full flex items-center justify-center gap-3 py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-200
              ${isLoading || !hasAnswer
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]'}
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                正在诊断...
              </>
            ) : (
              <>
                <Send className="w-6 h-6" />
                提交诊断
              </>
            )}
          </button>

          {!hasAnswer && (
            <p className="text-center text-sm text-gray-500">
              请先选择或输入你的答案
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

