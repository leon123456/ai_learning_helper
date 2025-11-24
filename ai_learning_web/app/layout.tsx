import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import NavBar from '@/components/NavBar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI 学习诊断助手',
  description: '智能学习诊断系统 - 拍照识别试题，AI 自动诊断错因，生成个性化练习',
  keywords: ['AI学习', '学习诊断', 'OCR识别', '智能教育'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
          <NavBar />
          <main className="container mx-auto px-4 py-8 max-w-6xl">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

