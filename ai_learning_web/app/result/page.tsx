'use client'

/**
 * 单题诊断结果页面
 * 
 * 功能：
 * 1. 显示诊断结果（正确/错误）
 * 2. 显示正确答案和解析
 * 3. 显示掌握度和学习建议
 * 4. 推荐练习题
 */

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  RefreshCw,
  CheckCircle,
  XCircle,
  Lightbulb,
  Target,
  BookOpen,
  ChevronRight,
  Sparkles,
} from 'lucide-react'
import { useAppStore } from '@/lib/store'

export default function ResultPage() {
  const router = useRouter()
  
  const {
    currentProblem,
    diagnoseResult,
    reset,
  } = useAppStore()

  // 如果没有诊断结果，跳转回上传页
  useEffect(() => {
    if (!diagnoseResult) {
      router.push('/upload')
    }
  }, [diagnoseResult, router])

  // 重新开始
  const handleRestart = () => {
    reset()
    router.push('/upload')
  }

  if (!diagnoseResult || !currentProblem) {
    return null
  }

  const { correct, correct_answer, user_answer, error_type, analysis, mastery_score, next_action, recommended_practice } = diagnoseResult

  // 掌握度颜色
  const getMasteryColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  // 掌握度描述
  const getMasteryLabel = (score: number) => {
    if (score >= 90) return '优秀'
    if (score >= 80) return '良好'
    if (score >= 60) return '一般'
    if (score >= 40) return '较弱'
    return '需加强'
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* 顶部导航 */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => router.push('/review')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>返回修改</span>
        </button>
        
        <button
          onClick={handleRestart}
          className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>新题目</span>
        </button>
      </div>

      {/* 结果卡片 */}
      <div className={`
        rounded-3xl p-8 mb-8 shadow-xl
        ${correct 
          ? 'bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 border-2 border-green-200' 
          : 'bg-gradient-to-br from-red-50 via-rose-50 to-pink-50 border-2 border-red-200'}
      `}>
        <div className="flex items-center justify-center mb-6">
          <div className={`
            w-24 h-24 rounded-full flex items-center justify-center shadow-lg
            ${correct ? 'bg-green-500' : 'bg-red-500'}
          `}>
            {correct ? (
              <CheckCircle className="w-12 h-12 text-white" />
            ) : (
              <XCircle className="w-12 h-12 text-white" />
            )}
          </div>
        </div>

        <h1 className={`text-3xl font-bold text-center mb-2 ${correct ? 'text-green-700' : 'text-red-700'}`}>
          {correct ? '回答正确！' : '回答错误'}
        </h1>
        
        {!correct && error_type && (
          <p className="text-center text-red-600 mb-4">
            错误类型: {error_type}
          </p>
        )}

        <div className="grid md:grid-cols-2 gap-4 mt-6">
          <div className="bg-white/70 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">你的答案</p>
            <p className={`text-lg font-semibold ${correct ? 'text-green-700' : 'text-red-700'}`}>
              {user_answer || '(未作答)'}
            </p>
          </div>
          <div className="bg-white/70 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">正确答案</p>
            <p className="text-lg font-semibold text-green-700">
              {correct_answer}
            </p>
          </div>
        </div>
      </div>

      {/* 详细分析 */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* 掌握度 */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <h2 className="font-semibold text-gray-900">掌握程度</h2>
          </div>

          <div className="flex items-center justify-between mb-3">
            <span className={`text-4xl font-bold ${getMasteryColor(mastery_score).split(' ')[0]}`}>
              {mastery_score}%
            </span>
            <span className={`px-4 py-2 rounded-full text-sm font-medium ${getMasteryColor(mastery_score)}`}>
              {getMasteryLabel(mastery_score)}
            </span>
          </div>

          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${
                mastery_score >= 80 ? 'bg-green-500' :
                mastery_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${mastery_score}%` }}
            />
          </div>
        </div>

        {/* 学习建议 */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <Lightbulb className="w-5 h-5 text-amber-600" />
            </div>
            <h2 className="font-semibold text-gray-900">学习建议</h2>
          </div>
          
          <p className="text-gray-700 leading-relaxed">
            {next_action}
          </p>
        </div>
      </div>

      {/* 解析 */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-blue-600" />
          </div>
          <h2 className="font-semibold text-gray-900">详细解析</h2>
        </div>
        
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {analysis}
          </p>
        </div>
      </div>

      {/* 推荐练习 */}
      {recommended_practice && recommended_practice.length > 0 && (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-indigo-600" />
            </div>
            <h2 className="font-semibold text-gray-900">推荐练习</h2>
          </div>
          
          <div className="space-y-3">
            {recommended_practice.map((practice, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl p-4 flex items-center justify-between hover:shadow-md transition-shadow cursor-pointer"
              >
                <div>
                  <p className="font-medium text-gray-900">{practice.knowledge}</p>
                  <p className="text-sm text-gray-500">
                    难度: {practice.difficulty === 'easy' ? '简单' : practice.difficulty === 'medium' ? '中等' : '困难'}
                    · 建议练习 {practice.count} 题
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 底部操作 */}
      <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={handleRestart}
          className="flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-xl hover:scale-105 transition-all"
        >
          <RefreshCw className="w-5 h-5" />
          继续练习新题目
        </button>
      </div>
    </div>
  )
}

