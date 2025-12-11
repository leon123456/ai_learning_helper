'use client'

/**
 * 批量诊断结果页面
 * 
 * 功能：
 * 1. 显示整体诊断摘要
 * 2. 显示每道题的诊断结果
 * 3. 显示薄弱知识点
 * 4. 提供学习建议
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  Trophy,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MinusCircle,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Lightbulb,
  BarChart3,
  RefreshCw,
} from 'lucide-react'
import { usePaperStore } from '@/lib/paper-store'
import { getQuestionTypeLabel } from '@/lib/paper-types'

export default function PaperResultPage() {
  const router = useRouter()
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set())
  
  const { diagnoseResult, ocrResult, reset } = usePaperStore()

  // 如果没有诊断结果，跳转回上传页
  useEffect(() => {
    if (!diagnoseResult) {
      router.push('/paper')
    }
  }, [diagnoseResult, router])

  // 切换展开/收起
  const toggleResult = (index: number) => {
    const newExpanded = new Set(expandedResults)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedResults(newExpanded)
  }

  // 重新开始
  const handleRestart = () => {
    reset()
    router.push('/paper')
  }

  if (!diagnoseResult) {
    return null
  }

  const { summary, results } = diagnoseResult

  // 计算正确率颜色
  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 80) return 'text-green-600'
    if (accuracy >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getAccuracyBg = (accuracy: number) => {
    if (accuracy >= 80) return 'from-green-500 to-emerald-500'
    if (accuracy >= 60) return 'from-yellow-500 to-orange-500'
    return 'from-red-500 to-rose-500'
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* 顶部导航 */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => router.push('/paper/review')}
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
          <span>重新开始</span>
        </button>
      </div>

      {/* 总体成绩卡片 */}
      <div className={`bg-gradient-to-r ${getAccuracyBg(summary.accuracy)} rounded-2xl p-6 text-white mb-6 shadow-lg`}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-1">诊断报告</h1>
            <p className="opacity-90">共诊断 {summary.total_questions} 道题目</p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold">{summary.accuracy.toFixed(0)}%</div>
            <div className="text-sm opacity-90">正确率</div>
          </div>
        </div>

        {/* 统计数据 */}
        <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/20">
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.correct_count}</div>
            <div className="text-xs opacity-80">正确</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.wrong_count}</div>
            <div className="text-xs opacity-80">错误</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.unanswered_count}</div>
            <div className="text-xs opacity-80">未作答</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.average_mastery.toFixed(0)}</div>
            <div className="text-xs opacity-80">平均掌握度</div>
          </div>
        </div>
      </div>

      {/* 按题型统计 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          按题型统计
        </h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(summary.stats_by_type).map(([type, stats]) => (
            <div key={type} className="p-4 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-900 mb-2">
                {getQuestionTypeLabel(type)}
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  {stats.correct}/{stats.total} 正确
                </span>
                <span className={`font-medium ${getAccuracyColor(stats.accuracy)}`}>
                  {stats.accuracy.toFixed(0)}%
                </span>
              </div>
              <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r ${getAccuracyBg(stats.accuracy)}`}
                  style={{ width: `${stats.accuracy}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 薄弱知识点 */}
      {summary.weak_knowledge_points.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            需要加强的知识点
          </h2>
          <div className="space-y-3">
            {summary.weak_knowledge_points.map((kp, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-100">
                <div>
                  <span className="font-medium text-gray-900">{kp.knowledge}</span>
                  <span className="ml-2 text-sm text-gray-500">
                    ({kp.error_count}/{kp.total_count} 错误)
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm text-amber-600">
                    建议练习 {kp.recommended_practice_count} 题
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 学习建议 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          学习建议
        </h2>
        <p className="text-gray-700 leading-relaxed">
          {summary.overall_suggestion}
        </p>
      </div>

      {/* 每道题的详细结果 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            详细诊断结果
          </h2>
        </div>

        <div className="divide-y divide-gray-100">
          {results.map((result, idx) => {
            const isExpanded = expandedResults.has(idx)
            const { diagnose_result } = result
            
            // 状态图标和颜色
            let StatusIcon = MinusCircle
            let statusColor = 'text-gray-500'
            let statusBg = 'bg-gray-50'
            
            if (diagnose_result.error_type === '未作答') {
              StatusIcon = MinusCircle
              statusColor = 'text-gray-500'
              statusBg = 'bg-gray-50'
            } else if (diagnose_result.correct) {
              StatusIcon = CheckCircle
              statusColor = 'text-green-600'
              statusBg = 'bg-green-50'
            } else {
              StatusIcon = XCircle
              statusColor = 'text-red-600'
              statusBg = 'bg-red-50'
            }

            return (
              <div key={idx}>
                {/* 题目标题 */}
                <div
                  className={`p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors ${statusBg}`}
                  onClick={() => toggleResult(idx)}
                >
                  <div className="flex items-center gap-3">
                    <StatusIcon className={`w-6 h-6 ${statusColor}`} />
                    <div>
                      <span className="font-medium text-gray-900">
                        第 {result.question_index + 1} 题
                      </span>
                      <span className="ml-2 text-sm text-gray-500">
                        掌握度: {diagnose_result.mastery_score}%
                      </span>
                    </div>
                  </div>
                  
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                {/* 详细内容 */}
                {isExpanded && (
                  <div className="px-4 pb-4 bg-gray-50">
                    {/* 题目内容 */}
                    <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
                      <div className="text-sm text-gray-500 mb-1">题目：</div>
                      <div className="text-gray-800">{result.question.question}</div>
                    </div>

                    {/* 答案对比 */}
                    <div className="grid sm:grid-cols-2 gap-4 mb-4">
                      <div className="p-3 bg-white rounded-lg border border-gray-200">
                        <div className="text-sm text-gray-500 mb-1">你的答案：</div>
                        <div className="text-gray-800">
                          {diagnose_result.user_answer || '(未作答)'}
                        </div>
                      </div>
                      <div className="p-3 bg-white rounded-lg border border-gray-200">
                        <div className="text-sm text-gray-500 mb-1">正确答案：</div>
                        <div className="text-green-600 font-medium">
                          {diagnose_result.correct_answer || '-'}
                        </div>
                      </div>
                    </div>

                    {/* 错误类型和分析 */}
                    {diagnose_result.error_type && diagnose_result.error_type !== '无' && (
                      <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-100">
                        <div className="text-sm font-medium text-red-700 mb-1">
                          错误类型：{diagnose_result.error_type}
                        </div>
                      </div>
                    )}

                    {/* 分析 */}
                    <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
                      <div className="text-sm text-gray-500 mb-1">解析：</div>
                      <div className="text-gray-700 whitespace-pre-wrap">
                        {diagnose_result.analysis}
                      </div>
                    </div>

                    {/* 建议 */}
                    {diagnose_result.next_action && (
                      <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                        <div className="text-sm font-medium text-indigo-700 mb-1">💡 学习建议：</div>
                        <div className="text-indigo-600">
                          {diagnose_result.next_action}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* 底部操作 */}
      <div className="mt-8 flex justify-center gap-4">
        <button
          onClick={handleRestart}
          className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
        >
          上传新试卷
        </button>
      </div>

      {/* 底部占位 */}
      <div className="h-8" />
    </div>
  )
}

