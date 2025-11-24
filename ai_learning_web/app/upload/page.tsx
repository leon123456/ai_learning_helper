'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Upload

Box from '@/components/UploadBox'
import LoadingSpinner from '@/components/LoadingSpinner'
import { parseImage, fileToBase64, isValidImage, formatErrorMessage } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { AlertCircle, CheckCircle } from 'lucide-react'

export default function UploadPage() {
  const router = useRouter()
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const { setCurrentImage, setOCRResult, setCurrentProblem, setLoading, isLoading } = useAppStore()

  const handleFileSelect = async (file: File) => {
    setError(null)
    
    try {
      // 1. 验证文件
      isValidImage(file)
      
      // 2. 生成预览
      const previewUrl = URL.createObjectURL(file)
      setPreview(previewUrl)
      setCurrentImage(previewUrl)
      
      // 3. 转换为 Base64
      setLoading(true)
      const base64 = await fileToBase64(file)
      
      // 4. 调用 OCR API
      console.log('📤 开始 OCR 识别...')
      const result = await parseImage({ image_base64: base64 })
      
      console.log('✅ OCR 识别成功:', result)
      setOCRResult(result)
      
      // 5. 检查是否识别到题目
      if (!result.problems || result.problems.length === 0) {
        setError('未识别到题目，请确保图片清晰且包含题目内容')
        setLoading(false)
        return
      }
      
      // 6. 设置第一个题目为当前题目
      setCurrentProblem(result.problems[0])
      
      // 7. 跳转到题目回显页面
      setLoading(false)
      router.push('/review')
      
    } catch (err) {
      const errorMsg = formatErrorMessage(err)
      console.error('❌ 上传失败:', errorMsg)
      setError(errorMsg)
      setLoading(false)
    }
  }

  const handleClearPreview = () => {
    setPreview(null)
    setCurrentImage(null)
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto animate-fadeIn">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-3">上传试卷图片</h1>
        <p className="text-gray-600">拖拽或点击上传图片，AI 将自动识别题目内容</p>
      </div>

      {/* 上传区域 */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
        <UploadBox
          onFileSelect={handleFileSelect}
          preview={preview}
          onClearPreview={handleClearPreview}
          isLoading={isLoading}
        />

        {/* 加载状态 */}
        {isLoading && (
          <div className="mt-8 py-8">
            <LoadingSpinner size="lg" text="正在识别题目，请稍候..." />
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-800">上传失败</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* 成功提示 */}
        {preview && !isLoading && !error && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-3">
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-green-800">图片上传成功</p>
              <p className="text-sm text-green-600 mt-1">点击"开始识别"按钮继续</p>
            </div>
          </div>
        )}
      </div>

      {/* 提示信息 */}
      <div className="mt-8 grid md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="font-medium text-blue-900 mb-1">📸 清晰拍摄</div>
          <div className="text-sm text-blue-700">确保题目文字清晰可见</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="font-medium text-purple-900 mb-1">📏 完整内容</div>
          <div className="text-sm text-purple-700">包含题目、选项和必要说明</div>
        </div>
        <div className="bg-pink-50 rounded-lg p-4">
          <div className="font-medium text-pink-900 mb-1">💡 支持格式</div>
          <div className="text-sm text-pink-700">JPG、PNG、WebP，最大10MB</div>
        </div>
      </div>
    </div>
  )
}

