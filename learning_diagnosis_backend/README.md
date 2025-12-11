# 学习诊断系统后端

智能学习诊断系统的后端服务，提供题目识别、诊断分析、学习规划等功能。

## 核心功能

### 1. 单题诊断
- OCR 识别（阿里云 + GPT Vision）
- 自动判题（支持客观题和主观题）
- 错因分析
- 掌握度评估
- 个性化学习建议

### 2. **试卷结构化识别与批量诊断** 🆕
- **智能切题** - 自动识别试卷中的所有题目
- **结构化识别** - 识别题干、选项、公式、图形
- **坐标定位** - 返回题目位置，支持前端高亮
- **批量诊断** - 一次性诊断整张试卷
- **智能报告** - 正确率、掌握度、薄弱知识点分析

### 3. 其他功能
- 教师助手（题目生成、评语生成）
- 学习规划（知识图谱、学习路径）

## 技术栈

- **框架**: FastAPI
- **OCR**: 
  - 阿里云 RecognizeEduQuestionOcr（单题识别）
  - 阿里云 RecognizeEduPaperStructed（试卷结构化识别） 🆕
  - OpenAI GPT-4o Vision（图形识别增强）
- **LLM**: Azure OpenAI / OpenAI / DeepSeek / Qwen
- **数据验证**: Pydantic

## 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# LLM 配置（选择一个）
PROVIDER=azure  # azure | openai | deepseek | qwen

# Azure OpenAI
AZURE_OPENAI_ENDPOINT_GPT4O2=https://your-endpoint.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY_GPT4O2=your_api_key
AZURE_OPENAI_DEPLOYMENT_GPT4O2=gpt-4o-2

# 阿里云 OCR 配置
ALIYUN_ACCESS_KEY_ID=LTAI5tRm...
ALIYUN_ACCESS_KEY_SECRET=your_secret
ALIYUN_OCR_ENDPOINT=cn-hangzhou.aliyuncs.com

# OCR 提供者（auto | aliyun | llm）
OCR_PROVIDER=auto
```

### 3. 启动服务

```bash
cd learning_diagnosis_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 单题相关

#### POST /api/v1/ocr/parse
OCR 识别并解析题目

**请求：**
```json
{
  "image_url": "https://example.com/question.jpg"
}
```

**响应：**
```json
{
  "raw_text": "识别的文本",
  "problems": [
    {
      "type": "choice",
      "question": "题目内容",
      "options": ["A...", "B...", "C...", "D..."],
      "knowledge_points": ["运动学"],
      "difficulty": "medium"
    }
  ]
}
```

#### POST /api/v1/diagnose
诊断单个题目

**请求：**
```json
{
  "problem": {
    "type": "choice",
    "question": "题目内容",
    "options": ["A...", "B...", "C...", "D..."]
  },
  "user_answer": "A"
}
```

**响应：**
```json
{
  "correct": true,
  "correct_answer": "A",
  "user_answer": "A",
  "error_type": "无",
  "analysis": "详细分析",
  "mastery_score": 95,
  "next_action": "学习建议",
  "recommended_practice": [...]
}
```

### 试卷相关 🆕

#### POST /api/v1/paper/recognize
试卷结构化识别

**请求：**
```json
{
  "image_url": "https://example.com/paper.jpg"
}
```

**响应：**
```json
{
  "paper_structure": {
    "page_id": 1,
    "width": 2377,
    "height": 3442,
    "part_info": [...],
    "figure": [...]
  },
  "questions": [
    {
      "index": 1,
      "type": "choice",
      "question": "题干",
      "options": ["A...", "B...", "C...", "D..."],
      "position": [...],
      "section_title": "选择题"
    }
  ],
  "total_questions": 10
}
```

#### POST /api/v1/paper/batch-diagnose
试卷批量诊断

**请求：**
```json
{
  "questions": [...],
  "answers": [
    {"question_index": 1, "user_answer": "A"},
    {"question_index": 2, "user_answer": "B"}
  ]
}
```

**响应：**
```json
{
  "results": [
    {
      "question_index": 1,
      "question": {...},
      "diagnose_result": {...}
    }
  ],
  "summary": {
    "total_questions": 10,
    "correct_count": 8,
    "accuracy": 80.0,
    "average_mastery": 75.5,
    "stats_by_type": {...},
    "weak_knowledge_points": [...],
    "overall_suggestion": "..."
  }
}
```

## 测试

### 单题诊断测试

```bash
# 测试单题 OCR
python test/test_url_only.py

# 测试完整诊断流程
python test/test_diagnostic.py
```

### 试卷识别测试 🆕

```bash
# 仅测试试卷识别
python test/test_paper_ocr.py

# 测试试卷识别 + 批量诊断
python test/test_paper_ocr.py --with-diagnose

# 使用自定义图片
python test/test_paper_ocr.py --image-url "https://your-image-url.com/paper.jpg"
```

## 项目结构

```
learning_diagnosis_backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes_ocr.py          # OCR 识别接口
│   │       ├── routes_diagnostic.py   # 单题诊断接口
│   │       ├── routes_paper.py        # 试卷识别和批量诊断接口 🆕
│   │       ├── routes_teacher.py      # 教师助手接口
│   │       └── routes_planner.py      # 学习规划接口
│   ├── core/
│   │   └── config.py                  # 配置管理
│   ├── schemas/
│   │   ├── ocr.py                     # OCR 数据模型
│   │   ├── diagnose.py                # 诊断数据模型
│   │   └── paper.py                   # 试卷数据模型 🆕
│   ├── services/
│   │   ├── llm.py                     # LLM 客户端
│   │   ├── ocr.py                     # OCR 服务（单题）
│   │   ├── aliyun_ocr.py              # 阿里云单题 OCR
│   │   ├── aliyun_paper_ocr.py        # 阿里云试卷 OCR 🆕
│   │   ├── diagnostic.py              # 诊断服务（单题）
│   │   └── paper_diagnostic.py        # 试卷诊断服务 🆕
│   └── main.py                        # 主应用
├── test/
│   ├── test_diagnostic.py             # 诊断测试
│   ├── test_paper_ocr.py              # 试卷识别测试 🆕
│   ├── 阿里云OCR测试总结.md
│   ├── 试卷结构化识别功能说明.md      🆕
│   └── API使用示例.md                  🆕
└── requirements.txt                    # 依赖包
```

## 配置说明

### OCR 提供者配置

在 `.env` 中设置 `OCR_PROVIDER`：

- `auto` - 优先阿里云，失败则回退 LLM（推荐）
- `aliyun` - 仅使用阿里云 OCR
- `llm` - 仅使用 LLM Vision

### 阿里云 RAM 权限

确保 AccessKey 对应的用户拥有以下权限：
- `AliyunOCRFullAccess` 或
- `AliyunOCRReadOnlyAccess`

## 文档

- [单题 OCR 测试总结](./test/阿里云OCR测试总结.md)
- [试卷结构化识别功能说明](./test/试卷结构化识别功能说明.md) 🆕
- [API 使用示例](./test/API使用示例.md) 🆕
- [项目设计文档](../project_design.md)

## 常见问题

### 1. 阿里云 OCR 401 错误
- 检查 AccessKey 配置是否正确
- 确认 RAM 权限已正确配置
- 等待 1-2 分钟让权限生效

### 2. 图片识别失败
- 确保图片 URL 公网可访问
- 建议使用图床（如 ImgBB）或阿里云 OSS
- 图片大小建议 < 2MB

### 3. LLM API 调用失败
- 检查 API Key 和 Endpoint 配置
- 确认网络连接正常
- 检查 API 配额是否用完

## 性能优化建议

1. **图片优化** - 压缩到 2MB 以内，保持清晰度
2. **批量控制** - 单次批量诊断建议不超过 20 题
3. **缓存机制** - 识别结果可以缓存
4. **异步处理** - 大批量任务使用异步队列

## 开发计划

- [x] 单题 OCR 识别
- [x] 单题诊断
- [x] 试卷结构化识别 🆕
- [x] 批量诊断 🆕
- [ ] 前端界面
- [ ] 题库集成
- [ ] 错题本功能
- [ ] 学习报告生成

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

