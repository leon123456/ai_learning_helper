'use client'

import Link from 'next/link'
import { Upload, Brain, Target, Sparkles, ArrowRight, FileImage, Layers } from 'lucide-react'

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
        
        {/* 两个上传入口 */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          {/* 单题上传 */}
          <Link
            href="/upload"
            className="group relative w-full sm:w-auto inline-flex items-center justify-center space-x-3 bg-white border-2 border-indigo-200 text-indigo-700 px-8 py-4 rounded-xl text-lg font-medium hover:border-indigo-400 hover:bg-indigo-50 hover:shadow-lg transition-all"
          >
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
              <Upload className="h-5 w-5" />
            </div>
            <div className="text-left">
              <span className="block font-semibold">上传单题</span>
              <span className="block text-sm text-gray-500 font-normal">拍一道题，快速诊断</span>
            </div>
            <ArrowRight className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity" />
          </Link>
          
          {/* 试卷上传 */}
          <Link
            href="/paper"
            className="group relative w-full sm:w-auto inline-flex items-center justify-center space-x-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-xl text-lg font-medium hover:shadow-xl hover:scale-105 transition-all"
          >
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <FileImage className="h-5 w-5" />
            </div>
            <div className="text-left">
              <span className="block font-semibold">上传试卷</span>
              <span className="block text-sm text-white/80 font-normal">整张试卷，批量诊断</span>
            </div>
            <ArrowRight className="h-5 w-5 opacity-70 group-hover:opacity-100 transition-opacity" />
          </Link>
        </div>
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
        <p className="text-gray-600 mb-8">选择适合你的方式，开始智能学习之旅</p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/upload"
            className="inline-flex items-center space-x-2 bg-white text-indigo-600 border-2 border-indigo-200 px-6 py-3 rounded-lg font-medium hover:bg-indigo-50 hover:border-indigo-300 transition-all"
          >
            <Upload className="h-5 w-5" />
            <span>单题诊断</span>
          </Link>
          <Link
            href="/paper"
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all"
          >
            <FileImage className="h-5 w-5" />
            <span>试卷批量诊断</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </div>
    </div>
  )
}

