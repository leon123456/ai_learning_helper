# AI 学习诊断系统 - Web 前端

## 📋 项目简介

AI 智能学习诊断系统的 Next.js 前端项目，提供拍照上传试卷、AI 自动识别题目、智能诊断错因、生成个性化练习等功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai_learning_web
npm install
```

### 2. 配置环境变量

创建 `.env.local` 文件：

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:3000`

### 4. 构建生产版本

```bash
npm run build
npm start
```

## 📁 项目结构

```
ai_learning_web/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # 根布局
│   ├── globals.css              # 全局样式
│   ├── page.tsx                 # 首页
│   ├── upload/                  # 上传页面
│   ├── review/                  # 题目回显与答题页面
│   ├── diagnose/                # 诊断结果页面
│   └── practice/                # 推荐练习页面
├── components/                   # React 组件
│   ├── NavBar.tsx               # 导航栏
│   ├── LoadingSpinner.tsx       # 加载动画
│   ├── UploadBox.tsx            # 上传组件
│   ├── OCRPreview.tsx           # OCR 结果展示
│   ├── AnswerInput.tsx          # 答案输入组件
│   ├── DiagnosisCard.tsx        # 诊断结果卡片
│   └── PracticeList.tsx         # 练习题列表
├── lib/                         # 工具函数
│   ├── api.ts                   # API 调用函数
│   ├── types.ts                 # TypeScript 类型定义
│   ├── utils.ts                 # 通用工具函数
│   └── store.ts                 # Zustand 状态管理
├── public/                      # 静态资源
└── package.json                 # 项目配置
```

## 🔄 用户流程

```
1. 首页 (/) → 2. 上传页面 (/upload)
                    ↓
3. 题目回显页面 (/review) → 4. 诊断结果 (/diagnose)
                                     ↓
                            5. 推荐练习 (/practice)
```

### 流程说明

1. **上传图片** `/upload`
   - 拖拽或点击上传试卷图片
   - 图片预览
   - 调用后端 `/api/v1/ocr/parse` 识别
   - 自动跳转到题目回显页面

2. **题目回显** `/review`
   - 展示 OCR 识别的题目内容
   - 数学公式渲染
   - 根据题型显示不同的答题界面：
     - 选择题：单选按钮
     - 填空题：文本输入框
     - 简答题：多行文本框
   - 提交后跳转到诊断页面

3. **诊断结果** `/diagnose`
   - 显示答案正确性
   - 错因分析
   - 掌握程度评分
   - 学习建议
   - 推荐练习按钮

4. **推荐练习** `/practice`
   - 调用 GPT 生成个性化练习题
   - 显示题目、选项、解析
   - 可直接在线练习

## 🛠️ 技术栈

### 核心框架
- **Next.js 14** - React 服务端渲染框架
- **React 18** - UI 库
- **TypeScript** - 类型安全

### UI 与样式
- **Tailwind CSS** - 原子化 CSS 框架
- **Lucide React** - 图标库
- **KaTeX** - 数学公式渲染

### 状态管理与请求
- **Zustand** - 轻量级状态管理
- **Axios** - HTTP 客户端
- **React Dropzone** - 文件上传

### 开发工具
- **ESLint** - 代码检查
- **PostCSS** - CSS 处理
- **Autoprefixer** - CSS 兼容性

## 📦 主要依赖

```json
{
  "next": "^14.2.0",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "tailwindcss": "^3.4.0",
  "zustand": "^4.5.0",
  "axios": "^1.6.0",
  "react-dropzone": "^14.2.0",
  "lucide-react": "^0.344.0",
  "katex": "^0.16.9"
}
```

## 🔌 API 集成

### 后端 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/ocr/parse` | POST | OCR 识别图片 |
| `/api/v1/diagnose` | POST | 学习诊断 |
| `/api/v1/generate-practice` | POST | 生成推荐练习 |
| `/health` | GET | 健康检查 |

### API 调用示例

```typescript
import { parseImage, diagnoseProblem, generatePractice } from '@/lib/api'

// OCR 识别
const ocrResult = await parseImage({
  image_base64: base64String
})

// 诊断
const diagnoseResult = await diagnoseProblem({
  problem: currentProblem,
  user_answer: '答案'
})

// 生成练习
const practices = await generatePractice({
  knowledge_points: ['科学记数法'],
  difficulty: 'easy',
  count: 3
})
```

## 🎨 组件说明

### `<NavBar />` - 导航栏
顶部导航栏，显示当前页面，支持响应式布局。

### `<UploadBox />` - 上传组件
支持拖拽上传、文件选择、图片预览、文件验证。

### `<OCRPreview />` - OCR 结果展示
显示识别的题目内容，支持 LaTeX 数学公式渲染。

### `<AnswerInput />` - 答案输入
根据题型自动切换输入方式（选择题/填空题/简答题）。

### `<DiagnosisCard />` - 诊断结果卡片
展示诊断结果，包括对错、分数、错因分析、建议。

### `<PracticeList />` - 练习题列表
显示推荐的练习题，支持查看答案和解析。

## 🌐 部署

### Vercel 部署（推荐）

1. 推送代码到 GitHub
2. 在 [Vercel](https://vercel.com) 导入项目
3. 添加环境变量 `NEXT_PUBLIC_API_URL`
4. 自动部署

### 手动部署

```bash
# 构建
npm run build

# 启动
npm start

# 或使用 PM2
pm2 start npm --name "ai-learning-web" -- start
```

## 🐛 故障排除

### OCR 识别失败
- 检查后端服务是否启动 (http://127.0.0.1:8000/health)
- 检查图片格式是否支持
- 检查图片大小是否小于 10MB

### 页面空白
- 检查 `.env.local` 是否正确配置
- 检查浏览器控制台错误
- 清除浏览器缓存

### 数学公式不显示
- 确保 KaTeX CSS 已正确加载
- 检查网络连接

## 📝 待办事项

- [ ] 添加用户登录系统
- [ ] 历史记录功能
- [ ] 数据可视化（知识点掌握度图表）
- [ ] 导出学习报告（PDF）
- [ ] 暗黑模式
- [ ] PWA 支持

## 📄 许可证

本项目仅供学习和演示使用。

---

**开发团队**: AI Learning Team  
**最后更新**: 2025-11-23

