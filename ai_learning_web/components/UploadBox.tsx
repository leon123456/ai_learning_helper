'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon, X } from 'lucide-react'
import Image from 'next/image'

interface UploadBoxProps {
  onFileSelect: (file: File) => void
  preview?: string | null
  onClearPreview?: () => void
  isLoading?: boolean
}

export default function UploadBox({ 
  onFileSelect, 
  preview, 
  onClearPreview, 
  isLoading 
}: UploadBoxProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: isLoading,
  })

  // 如果有预览图，显示预览
  if (preview) {
    return (
      <div className="relative">
        <div className="relative w-full h-96 rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-50">
          <Image
            src={preview}
            alt="上传的图片预览"
            fill
            className="object-contain"
          />
        </div>
        {onClearPreview && !isLoading && (
          <button
            onClick={onClearPreview}
            className="absolute top-4 right-4 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors shadow-lg"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
    )
  }

  // 显示上传区域
  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all
        ${isDragActive 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }
        ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />
      
      <div className="flex flex-col items-center space-y-4">
        {isDragActive ? (
          <>
            <ImageIcon className="h-16 w-16 text-blue-500" />
            <p className="text-lg text-blue-600 font-medium">松开鼠标上传图片</p>
          </>
        ) : (
          <>
            <Upload className="h-16 w-16 text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700 mb-2">
                拖拽图片到此处，或点击上传
              </p>
              <p className="text-sm text-gray-500">
                支持 JPG、PNG、WebP 格式，最大 10MB
              </p>
            </div>
            <button
              type="button"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              disabled={isLoading}
            >
              选择文件
            </button>
          </>
        )}
      </div>
    </div>
  )
}

