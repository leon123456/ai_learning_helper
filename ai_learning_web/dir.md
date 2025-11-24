ai-learning-web/
│
├── package.json
├── next.config.js
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── .eslintrc.json
├── .gitignore
│
├── app/
│   ├── layout.tsx
│   ├── globals.css
│   │
│   ├── page.tsx                    # 首页：上传题目
│   │
│   ├── upload/
│   │   └── page.tsx                # 上传图片页面（拖拽+预览）
│   │
│   ├── review/
│   │   └── page.tsx                # OCR 解析结果展示 + 输入答案
│   │
│   ├── diagnose/
│   │   └── page.tsx                # 调用后端 /diagnose，展示诊断结果
│   │
│   ├── practice/
│   │   └── page.tsx                # GPT 推荐练习题展示页面
│
├── components/
│   ├── UploadBox.tsx               # 拖拽上传组件
│   ├── ImagePreview.tsx            # 图片预览
│   ├── OCRPreview.tsx              # OCR 提取结果展示模块
│   ├── AnswerInput.tsx             # 用户输入答案
│   ├── DiagnosisCard.tsx           # 诊断结果 UI
│   ├── PracticeList.tsx            # 推荐练习题 UI
│   ├── NavBar.tsx                  # 顶部导航
│   └── LoadingSpinner.tsx          # Loading 动画
│
├── lib/
│   ├── api.ts                      # 封装 FastAPI 请求的函数
│   └── types.ts                    # 类型定义（OCR、题目、诊断结果）
│
├── public/
│   ├── logo.png
│   └── placeholder.png
│
└── styles/
    └── shadcn.css                  # Shadcn/ui 组件样式



页面功能说明
1. /upload 上传页面

拖拽文件上传

自动预览图片

文件上传后发送到后端 /ocr/parse

跳转到 /review

2. /review 题目回显页面

显示题干 & 选项

用户输入自己的答案

点击“开始诊断” → 调用 /diagnose

跳转到 /diagnose

3. /diagnose 诊断页面

展示：

正确 / 错误

正确答案

用户答案

错误类型（概念错误 / 粗心等）

掌握分数

推荐学习方向

并提供按钮：

获取推荐练习 →

4. /practice GPT 推荐题目页面

自动调用 GPT-5.1 生成 2~5 个练习题

显示题目 + 解析

可以继续练习