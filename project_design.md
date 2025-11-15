learning_diagnosis_backend/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                 # FastAPI 入口
│  ├─ core/
│  │  ├─ config.py            # 配置（API key、环境变量等）
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ deps.py              # 依赖注入（DB、LLM client等）
│  │  └─ v1/
│  │     ├─ __init__.py
│  │     ├─ routes_ocr.py         # /ocr 相关接口
│  │     ├─ routes_diagnostic.py  # /diagnose 相关接口
│  │     ├─ routes_teacher.py     # /teacher 相关接口
│  │     ├─ routes_planner.py     # /planner 相关接口
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ llm.py               # 大模型统一封装
│  │  ├─ ocr.py               # OCR / 题目解析 Pipeline
│  │  ├─ diagnostic.py        # 学习诊断逻辑
│  │  ├─ planner.py           # 学习路径规划逻辑
│  │  └─ teacher.py           # AI 教师逻辑
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ student.py           # 学生画像（ORM or 简单类）
│  │  ├─ problem.py           # 题目模型
│  │  └─ session.py           # 学习会话（可选）
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ ocr.py               # 请求/响应 Pydantic 模型
│  │  ├─ diagnostic.py
│  │  ├─ planner.py
│  │  └─ teacher.py
│  ├─ prompt/
│  │  ├─ parser.md            # 题目解析 Agent Prompt
│  │  ├─ diagnose.md          # 诊断 Agent Prompt
│  │  ├─ planner.md           # 学习路径 Agent Prompt
│  │  ├─ teacher.md           # 教师 Agent Prompt
│  │  ├─ misconception.md     # 错误模式 Agent Prompt
│  │  ├─ generator.md         # 出题 Agent Prompt
│  │  └─ socratic.md          # 逐步提示 Agent Prompt
│  └─ data/
│     └─ knowledge_points.json  # 知识点体系（先简单放 JSON）
├─ requirements.txt
├─ .env.example
└─ README.md
