'use client'

import Link from 'next/link'
import { Upload, Brain, Target, Sparkles, ArrowRight } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="animate-fadeIn">
      {/* Hero Section */}
      <div className="text-center py-12 md:py-20">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          AI 智能学习诊断系统
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
          拍照识别试题 · AI 自动诊断错因 · 生成个性化练习
        </p>
        <Link
          href="/upload"
          className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:shadow-lg hover:scale-105 transition-all"
        >
          <Upload className="h-5 w-5" />
          <span>开始上传题目</span>
          <ArrowRight className="h-5 w-5" />
        </Link>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-8 mt-16">
        <div className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
          <div className="bg-blue-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <Upload className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3">智能识别</h3>
          <p className="text-gray-600">
            使用阿里云 OCR 技术，精准识别试卷内容，支持数学公式、选择题、填空题等多种题型。
          </p>
        </div>

        <div className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
          <div className="bg-purple-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <Brain className="h-6 w-6 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3">AI 诊断</h3>
          <p className="text-gray-600">
            GPT-5.1 自动判断答案正误，深度分析错因类型，提供详细的知识点诊断和学习建议。
          </p>
        </div>

        <div className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
          <div className="bg-pink-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <Target className="h-6 w-6 text-pink-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3">个性化练习</h3>
          <p className="text-gray-600">
            根据你的错误类型和掌握程度，AI 自动生成针对性练习题，帮助你快速提升。
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="mt-24">
        <h2 className="text-3xl font-bold text-center mb-12">使用流程</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { step: '1', title: '上传图片', desc: '拍照或上传试卷图片', icon: Upload },
            { step: '2', title: 'AI 识别', desc: 'OCR 自动识别题目内容', icon: Sparkles },
            { step: '3', title: '输入答案', desc: '填写你的解答', icon: Brain },
            { step: '4', title: '获取诊断', desc: '查看错因分析和练习推荐', icon: Target },
          ].map((item) => {
            const Icon = item.icon
            return (
              <div key={item.step} className="text-center">
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4 shadow-lg">
                  {item.step}
                </div>
                <h4 className="font-semibold text-lg mb-2">{item.title}</h4>
                <p className="text-gray-600 text-sm">{item.desc}</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* CTA */}
      <div className="mt-24 text-center bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-12">
        <h2 className="text-3xl font-bold mb-4">准备好提升成绩了吗？</h2>
        <p className="text-gray-600 mb-8">现在就开始你的智能学习之旅</p>
        <Link
          href="/upload"
          className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:shadow-lg hover:scale-105 transition-all"
        >
          <span>立即开始</span>
          <ArrowRight className="h-5 w-5" />
        </Link>
      </div>
    </div>
  )
}

