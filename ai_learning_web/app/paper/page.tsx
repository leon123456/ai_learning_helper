'use client'

/**
 * 试卷上传页面
 * 
 * 功能：
 * 1. 上传整张试卷图片
 * 2. 调用试卷结构化识别 API
 * 3. 跳转到题目列表页面
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileImage, Loader2, AlertCircle, CheckCircle, Sparkles } from 'lucide-react'
import { usePaperStore } from '@/lib/paper-store'
import { recognizePaper, fileToBase64Raw, fileToBase64WithPrefix, validatePaperImage } from '@/lib/paper-api'

export default function PaperUploadPage() {
  const router = useRouter()
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  
  const {
    setPaperImage,
    setPaperImageBase64,
    setOCRResult,
    setRecognizing,
    isRecognizing,
  } = usePaperStore()

  // 处理文件选择
  const handleFileSelect = async (file: File) => {
    setError(null)
    
    try {
      // 1. 验证文件
      validatePaperImage(file)
      
      // 2. 生成预览
      const previewUrl = await fileToBase64WithPrefix(file)
      setPreview(previewUrl)
      
      // 3. 开始识别
      setRecognizing(true)
      setPaperImage(previewUrl)
      
      // 4. 转换为 base64 并调用 API
      console.log('📤 开始试卷识别...')
      const base64 = await fileToBase64Raw(file)
      
      const result = await recognizePaper({ image_base64: base64 })
      console.log('✅ 试卷识别成功:', result)
      console.log('📊 题目数量:', result.questions?.length)
      
      // 5. 检查识别结果
      if (!result.questions || result.questions.length === 0) {
        setError('未识别到题目，请确保图片清晰且包含完整的试卷内容')
        setRecognizing(false)
        return
      }
      
      // 6. 保存结果
      console.log('💾 保存结果到 store...')
      setOCRResult(result)
      setPaperImageBase64(base64)  // 保存 base64 以便后续使用
      console.log('✅ Store 更新完成，题目数:', result.questions.length)
      
      // 7. 跳转到题目列表
      console.log('🚀 准备跳转到 /paper/review...')
      setRecognizing(false)
      
      // 使用 setTimeout 确保状态更新完成后再跳转
      setTimeout(() => {
        console.log('🔄 执行跳转...')
        router.push('/paper/review')
      }, 100)
      
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '上传失败，请重试'
      console.error('❌ 上传失败:', errorMsg)
      setError(errorMsg)
      setRecognizing(false)
    }
  }

  // 处理拖拽
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  // 处理点击上传
  const handleClick = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        handleFileSelect(file)
      }
    }
    input.click()
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* 标题 */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mb-4 shadow-lg">
          <FileImage className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          上传试卷
        </h1>
        <p className="text-gray-600">
          上传整张试卷图片，AI 将自动切题并识别内容
        </p>
      </div>

      {/* 上传区域 */}
      <div 
        className={`
          relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer
          ${isDragging 
            ? 'border-indigo-500 bg-indigo-50' 
            : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'}
          ${isRecognizing ? 'pointer-events-none opacity-60' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={!isRecognizing ? handleClick : undefined}
      >
        {/* 预览图 */}
        {preview && (
          <div className="absolute inset-4 rounded-xl overflow-hidden bg-gray-100">
            <img 
              src={preview} 
              alt="预览" 
              className="w-full h-full object-contain"
            />
            {/* 识别中遮罩 */}
            {isRecognizing && (
              <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-white">
                <Loader2 className="w-12 h-12 animate-spin mb-4" />
                <p className="text-lg font-medium">正在识别试卷...</p>
                <p className="text-sm opacity-80 mt-1">这可能需要 10-30 秒</p>
              </div>
            )}
          </div>
        )}

        {/* 上传提示 */}
        {!preview && (
          <div className="flex flex-col items-center">
            <div className={`
              w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-colors
              ${isDragging ? 'bg-indigo-100' : 'bg-gray-100'}
            `}>
              <Upload className={`w-10 h-10 ${isDragging ? 'text-indigo-600' : 'text-gray-400'}`} />
            </div>
            <p className="text-lg font-medium text-gray-700 mb-1">
              拖拽图片到这里，或点击上传
            </p>
            <p className="text-sm text-gray-500">
              支持 JPG、PNG、WebP 格式，最大 10MB
            </p>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">识别失败</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* 功能说明 */}
      <div className="mt-8 grid md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
            <Sparkles className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">智能切题</h3>
          <p className="text-sm text-gray-600">自动识别题号，智能分割每道题目</p>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-100">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
            <FileImage className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">配图识别</h3>
          <p className="text-sm text-gray-600">识别题目中的图形、表格并标注位置</p>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5 border border-green-100">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">批量诊断</h3>
          <p className="text-sm text-gray-600">一次性诊断整张试卷，生成学习报告</p>
        </div>
      </div>

      {/* 使用提示 */}
      <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
        <h4 className="font-medium text-amber-800 mb-2">💡 拍照建议</h4>
        <ul className="text-sm text-amber-700 space-y-1">
          <li>• 确保试卷平整，避免折痕和阴影</li>
          <li>• 保持题目完整，不要截断题干或选项</li>
          <li>• 光线充足，文字清晰可读</li>
          <li>• 如有手写答案，确保字迹清晰</li>
        </ul>
      </div>
    </div>
  )
}

