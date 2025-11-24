# AI 学习诊断系统 - Web 前端项目创建说明

## ✅ 已创建的文件

### 1. 项目配置文件
- ✅ `package.json` - 项目依赖和脚本
- ✅ `next.config.js` - Next.js 配置
- ✅ `tailwind.config.js` - Tailwind CSS 配置
- ✅ `postcss.config.js` - PostCSS 配置
- ✅ `tsconfig.json` - TypeScript 配置
- ✅ `.eslintrc.json` - ESLint 配置
- ✅ `.gitignore` - Git 忽略文件

### 2. 核心库文件
- ✅ `lib/types.ts` - TypeScript 类型定义
- ✅ `lib/api.ts` - API 调用函数
- ✅ `lib/utils.ts` - 工具函数
- ✅ `lib/store.ts` - Zustand 状态管理

### 3. 样式和布局
- ✅ `app/globals.css` - 全局样式
- ✅ `app/layout.tsx` - 根布局

### 4. 页面
- ✅ `app/page.tsx` - 首页
- ✅ `app/upload/page.tsx` - 上传页面

### 5. 组件
- ✅ `components/NavBar.tsx` - 导航栏
- ✅ `components/LoadingSpinner.tsx` - 加载动画
- ✅ `components/UploadBox.tsx` - 上传组件

### 6. 文档
- ✅ `README.md` - 项目文档
- ✅ `SETUP.md` - 本文档

## 📝 待创建的文件（按优先级）

### 高优先级（核心功能）

1. **OCR 结果展示组件** `components/OCRPreview.tsx`
2. **答案输入组件** `components/AnswerInput.tsx`
3. **题目回显页面** `app/review/page.tsx`
4. **诊断结果组件** `components/DiagnosisCard.tsx`
5. **诊断页面** `app/diagnose/page.tsx`

### 中优先级（扩展功能）

6. **练习题列表组件** `components/PracticeList.tsx`
7. **练习页面** `app/practice/page.tsx`

### 低优先级（优化）

8. **图片预览组件** `components/ImagePreview.tsx`（可选，已包含在 UploadBox 中）

## 🚀 快速启动指南

### 步骤 1: 安装依赖

```bash
cd /Users/liang/Documents/Github/AI_learning_helper/ai_learning_web
npm install
```

**预计安装时间**: 2-5 分钟

### 步骤 2: 创建环境变量

创建 `.env.local` 文件：

```bash
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
```

### 步骤 3: 启动后端服务

在另一个终端中：

```bash
cd /Users/liang/Documents/Github/AI_learning_helper/learning_diagnosis_backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### 步骤 4: 启动前端开发服务器

```bash
cd /Users/liang/Documents/Github/AI_learning_helper/ai_learning_web
npm run dev
```

访问: http://localhost:3000

## 📋 剩余文件创建清单

### 必须完成（核心功能）

#### 1. OCR 结果展示组件
**文件**: `components/OCRPreview.tsx`

**功能**:
- 显示识别的题目内容
- 渲染数学公式（LaTeX）
- 展示题目选项

#### 2. 答案输入组件
**文件**: `components/AnswerInput.tsx`

**功能**:
- 根据题型切换输入方式
- 选择题 → 单选/多选
- 填空题 → 文本输入
- 简答题 → 多行文本

#### 3. 题目回显页面
**文件**: `app/review/page.tsx`

**功能**:
- 显示 OCR 识别的题目
- 用户输入答案
- 提交诊断

#### 4. 诊断结果组件
**文件**: `components/DiagnosisCard.tsx`

**功能**:
- 展示诊断结果
- 对错、分数、错因
- 学习建议

#### 5. 诊断页面
**文件**: `app/diagnose/page.tsx`

**功能**:
- 调用诊断 API
- 显示诊断结果
- 跳转到练习推荐

### 可选完成（扩展功能）

#### 6. 练习题列表组件
**文件**: `components/PracticeList.tsx`

**功能**:
- 显示推荐练习题
- 查看答案和解析

#### 7. 练习页面
**文件**: `app/practice/page.tsx`

**功能**:
- 生成推荐练习
- 在线作答

## 🎯 当前状态

### 已完成 (60%)
- ✅ 项目基础配置
- ✅ API 调用层
- ✅ 状态管理
- ✅ 首页
- ✅ 上传功能

### 进行中 (30%)
- 🔄 题目回显页面
- 🔄 诊断页面
- 🔄 核心组件

### 未开始 (10%)
- ⏸️ 练习推荐页面
- ⏸️ 历史记录
- ⏸️ 数据可视化

## 🐛 已知问题

1. **KaTeX 导入问题**
   - `app/globals.css` 中的 `@import '~katex/dist/katex.min.css'` 可能需要改为直接从 node_modules 导入
   - 解决方案: 在 `app/layout.tsx` 中导入或使用 CDN

2. **Image 组件警告**
   - Next.js Image 组件需要配置外部图片域名
   - 已在 `next.config.js` 中配置

## 📚 下一步行动

### 立即执行（今天）

1. **安装依赖**
   ```bash
   cd ai_learning_web
   npm install
   ```

2. **测试当前功能**
   ```bash
   npm run dev
   ```
   - 访问首页
   - 测试上传功能

3. **创建剩余的核心页面和组件**（按上述清单）

### 本周计划

- 完成题目回显页面
- 完成诊断功能
- 端到端测试

### 下周计划

- 添加练习推荐功能
- UI/UX 优化
- 部署到 Vercel

## 💡 开发提示

### 调试技巧

1. **查看 API 调用**
   - 打开浏览器开发者工具 → Network 标签
   - 查看请求和响应

2. **查看状态**
   - 使用 Zustand DevTools
   - 或在组件中 `console.log(useAppStore.getState())`

3. **样式调试**
   - 使用 Tailwind CSS IntelliSense 插件
   - 浏览器开发者工具 → Elements

### 常见错误

1. **"Cannot find module"**
   - 检查文件路径是否正确
   - 检查 `tsconfig.json` 中的 paths 配置

2. **"Hydration failed"**
   - 确保客户端组件使用 `'use client'`
   - 检查服务端和客户端渲染不一致

3. **API 调用失败**
   - 检查后端服务是否启动
   - 检查 `.env.local` 配置
   - 查看浏览器 Console 错误

## 📞 支持

如果遇到问题:
1. 查看 `README.md` 中的故障排除部分
2. 检查浏览器 Console 和 Network 标签
3. 查看后端日志

## ✨ 项目亮点

- ✅ 完整的 TypeScript 类型支持
- ✅ 响应式设计（移动端友好）
- ✅ 优雅的加载和错误处理
- ✅ 现代化的 UI/UX
- ✅ 可扩展的架构

---

**创建时间**: 2025-11-23
**状态**: 骨架完成，等待核心页面开发
**预计完成**: 1-2 周

