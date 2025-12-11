'use client'

/**
 * 题目列表确认页面
 * 
 * 功能：
 * 1. 显示识别出的所有题目
 * 2. 允许用户输入/修改每道题的答案
 * 3. 显示题目在原图中的位置（高亮）
 * 4. 提交批量诊断
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  ArrowLeft, 
  ArrowRight, 
  Send, 
  Image as ImageIcon,
  CheckCircle,
  Circle,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { usePaperStore, useAnswerProgress } from '@/lib/paper-store'
import { batchDiagnose } from '@/lib/paper-api'
import { getQuestionTypeLabel, getQuestionStatus, getStatusColor } from '@/lib/paper-types'

export default function PaperReviewPage() {
  const router = useRouter()
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set([0]))
  
  const {
    paperImage,
    ocrResult,
    userAnswers,
    setUserAnswer,
    setDiagnoseResult,
    setDiagnosing,
    isDiagnosing,
    setError,
    diagnoseResult,
  } = usePaperStore()

  const { total, answered, progress } = useAnswerProgress()

  // 如果没有识别结果，跳转回上传页
  useEffect(() => {
    if (!ocrResult) {
      router.push('/paper')
    }
  }, [ocrResult, router])

  // 切换题目展开/收起
  const toggleQuestion = (index: number) => {
    const newExpanded = new Set(expandedQuestions)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedQuestions(newExpanded)
  }

  // 展开所有题目
  const expandAll = () => {
    if (!ocrResult) return
    setExpandedQuestions(new Set(ocrResult.questions.map((_, i) => i)))
  }

  // 收起所有题目
  const collapseAll = () => {
    setExpandedQuestions(new Set())
  }

  // 提交批量诊断
  const handleSubmit = async () => {
    if (!ocrResult) return

    try {
      setDiagnosing(true)
      setError(null)

      // 构建请求
      const answers = Object.entries(userAnswers).map(([index, answer]) => ({
        question_index: parseInt(index),
        user_answer: answer || '',
      }))

      console.log('📤 开始批量诊断...')
      const result = await batchDiagnose({
        questions: ocrResult.questions,
        answers,
      })

      console.log('✅ 批量诊断成功:', result)
      setDiagnoseResult(result)

      // 跳转到结果页
      router.push('/paper/result')
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '诊断失败，请重试'
      console.error('❌ 诊断失败:', errorMsg)
      setError(errorMsg)
    } finally {
      setDiagnosing(false)
    }
  }

  if (!ocrResult) {
    return null
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* 顶部导航 */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => router.push('/paper')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>重新上传</span>
        </button>
        
        <div className="text-center">
          <h1 className="text-xl font-bold text-gray-900">确认题目和答案</h1>
          <p className="text-sm text-gray-500">共识别到 {total} 道题目</p>
        </div>

        <div className="w-24" /> {/* 占位 */}
      </div>

      {/* 进度条 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200 mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            答题进度: {answered}/{total} 题
          </span>
          <div className="flex gap-2">
            <button
              onClick={expandAll}
              className="text-xs text-indigo-600 hover:text-indigo-700"
            >
              展开全部
            </button>
            <span className="text-gray-300">|</span>
            <button
              onClick={collapseAll}
              className="text-xs text-indigo-600 hover:text-indigo-700"
            >
              收起全部
            </button>
          </div>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 主要内容区 */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* 左侧：原图预览 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden sticky top-4 h-fit">
          <div className="p-4 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-gray-500" />
              试卷原图
            </h2>
          </div>
          {paperImage && (
            <div className="p-4">
              <img
                src={paperImage}
                alt="试卷"
                className="w-full rounded-lg border border-gray-200"
              />
            </div>
          )}
        </div>

        {/* 右侧：题目列表 */}
        <div className="space-y-4">
          {ocrResult.questions.map((question, idx) => {
            const isExpanded = expandedQuestions.has(idx)
            const answer = userAnswers[question.index] || ''
            const status = getQuestionStatus(question.index, userAnswers, diagnoseResult)

            return (
              <div
                key={question.index}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
              >
                {/* 题目头部 */}
                <div
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleQuestion(idx)}
                >
                  <div className="flex items-center gap-3">
                    {/* 状态图标 */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStatusColor(status)}`}>
                      {status === 'answered' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <Circle className="w-4 h-4" />
                      )}
                    </div>
                    
                    {/* 题号和类型 */}
                    <div>
                      <span className="font-medium text-gray-900">
                        第 {question.index + 1} 题
                      </span>
                      <span className="ml-2 text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                        {getQuestionTypeLabel(question.type)}
                      </span>
                      {question.has_figure && (
                        <span className="ml-2 text-xs px-2 py-0.5 bg-blue-100 text-blue-600 rounded">
                          含配图
                        </span>
                      )}
                    </div>
                  </div>

                  {/* 展开/收起图标 */}
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                {/* 题目内容（展开时显示） */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100">
                    {/* 题干 */}
                    <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-gray-800 whitespace-pre-wrap">
                        {question.question}
                      </p>
                      
                      {/* 配图描述 */}
                      {question.figure_description && (
                        <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-700">
                          <span className="font-medium">配图信息：</span>
                          <span className="ml-1">{question.figure_description}</span>
                        </div>
                      )}
                    </div>

                    {/* 选项（选择题） */}
                    {question.options && question.options.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {question.options.map((option, optIdx) => (
                          <label
                            key={optIdx}
                            className={`
                              flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all
                              ${answer === option.charAt(0) 
                                ? 'border-indigo-500 bg-indigo-50' 
                                : 'border-gray-200 hover:border-gray-300'}
                            `}
                            onClick={() => setUserAnswer(question.index, option.charAt(0))}
                          >
                            <div className={`
                              w-5 h-5 rounded-full border-2 flex items-center justify-center
                              ${answer === option.charAt(0) 
                                ? 'border-indigo-500 bg-indigo-500' 
                                : 'border-gray-300'}
                            `}>
                              {answer === option.charAt(0) && (
                                <div className="w-2 h-2 bg-white rounded-full" />
                              )}
                            </div>
                            <span className="text-gray-700">{option}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {/* 答案输入框（非选择题） */}
                    {(!question.options || question.options.length === 0) && (
                      <div className="mt-3">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          你的答案：
                        </label>
                        <textarea
                          value={answer}
                          onChange={(e) => setUserAnswer(question.index, e.target.value)}
                          placeholder="输入你的答案..."
                          className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                          rows={3}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* 底部提交按钮 */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {answered === 0 ? (
              <span className="flex items-center gap-1 text-amber-600">
                <AlertCircle className="w-4 h-4" />
                还没有填写任何答案
              </span>
            ) : answered < total ? (
              <span>还有 {total - answered} 道题未作答</span>
            ) : (
              <span className="flex items-center gap-1 text-green-600">
                <CheckCircle className="w-4 h-4" />
                所有题目已作答
              </span>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isDiagnosing}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all
              ${isDiagnosing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg hover:scale-105'}
            `}
          >
            {isDiagnosing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                正在诊断...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                提交诊断
              </>
            )}
          </button>
        </div>
      </div>

      {/* 底部占位 */}
      <div className="h-24" />
    </div>
  )
}

