# 试卷识别与批量诊断 API 使用示例

## 快速开始

### 1. 启动后端服务

```bash
cd learning_diagnosis_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## API 调用示例

### 示例 1：试卷识别（Python）

```python
import requests

# API 地址
API_BASE = "http://localhost:8000/api/v1"

# 1. 调用试卷识别 API
response = requests.post(
    f"{API_BASE}/paper/recognize",
    json={
        "image_url": "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"
    }
)

# 2. 获取识别结果
result = response.json()

print(f"识别到 {result['total_questions']} 道题目")

# 3. 查看第一道题
first_question = result['questions'][0]
print(f"\n题目 {first_question['index']}:")
print(f"类型: {first_question['type']}")
print(f"题干: {first_question['question']}")
if first_question['options']:
    print("选项:")
    for opt in first_question['options']:
        print(f"  {opt}")

# 4. 保存题目列表供后续使用
questions = result['questions']
```

### 示例 2：批量诊断（Python）

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# 假设已经从识别结果中获得了题目列表
questions = [...]  # 来自上一步

# 用户答案（模拟）
answers = [
    {"question_index": 1, "user_answer": "A"},
    {"question_index": 2, "user_answer": "B"},
    {"question_index": 3, "user_answer": "C"},
    {"question_index": 4, "user_answer": ""},  # 未作答
]

# 调用批量诊断 API
response = requests.post(
    f"{API_BASE}/paper/batch-diagnose",
    json={
        "questions": questions,
        "answers": answers
    }
)

# 获取诊断结果
result = response.json()
summary = result['summary']

# 打印整体统计
print("\n=== 诊断报告 ===")
print(f"总题数: {summary['total_questions']}")
print(f"已作答: {summary['answered_questions']}")
print(f"正确: {summary['correct_count']}")
print(f"错误: {summary['wrong_count']}")
print(f"未作答: {summary['unanswered_count']}")
print(f"正确率: {summary['accuracy']:.1f}%")
print(f"平均掌握度: {summary['average_mastery']:.1f}%")

# 打印按题型统计
print("\n=== 按题型统计 ===")
for q_type, stats in summary['stats_by_type'].items():
    print(f"\n{q_type}:")
    print(f"  正确率: {stats['accuracy']:.1f}%")
    print(f"  ({stats['correct']}/{stats['total']})")

# 打印薄弱知识点
if summary['weak_knowledge_points']:
    print("\n=== 薄弱知识点 ===")
    for weak_kp in summary['weak_knowledge_points']:
        print(f"\n{weak_kp['knowledge']}:")
        print(f"  正确率: {weak_kp['accuracy']:.1f}%")
        print(f"  建议练习: {weak_kp['recommended_practice_count']} 题")

# 打印总体建议
print(f"\n=== 学习建议 ===")
print(summary['overall_suggestion'])

# 查看某道题的详细诊断
first_result = result['results'][0]
diagnose = first_result['diagnose_result']
print(f"\n=== 题目 {first_result['question_index']} 详细诊断 ===")
print(f"用户答案: {diagnose['user_answer']}")
print(f"正确答案: {diagnose['correct_answer']}")
print(f"是否正确: {'✅' if diagnose['correct'] else '❌'}")
print(f"错误类型: {diagnose['error_type']}")
print(f"掌握度: {diagnose['mastery_score']}%")
print(f"分析: {diagnose['analysis']}")
print(f"建议: {diagnose['next_action']}")
```

### 示例 3：完整流程（JavaScript/TypeScript）

```javascript
// 试卷识别与批量诊断完整流程

const API_BASE = "http://localhost:8000/api/v1";

// 1. 上传试卷并识别
async function recognizePaper(imageUrl) {
  const response = await fetch(`${API_BASE}/paper/recognize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_url: imageUrl
    })
  });
  
  const result = await response.json();
  return result;
}

// 2. 批量诊断
async function batchDiagnose(questions, answers) {
  const response = await fetch(`${API_BASE}/paper/batch-diagnose`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      questions: questions,
      answers: answers
    })
  });
  
  const result = await response.json();
  return result;
}

// 3. 完整使用流程
async function main() {
  try {
    // 步骤1：识别试卷
    console.log('正在识别试卷...');
    const recognizeResult = await recognizePaper(
      "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"
    );
    
    console.log(`识别到 ${recognizeResult.total_questions} 道题目`);
    
    // 显示题目列表给用户
    const questions = recognizeResult.questions;
    questions.forEach((q, index) => {
      console.log(`\n题目 ${q.index}: ${q.question.substring(0, 50)}...`);
    });
    
    // 步骤2：用户作答（这里模拟）
    const userAnswers = [
      { question_index: 1, user_answer: "A" },
      { question_index: 2, user_answer: "B" },
      { question_index: 3, user_answer: "" }, // 未作答
    ];
    
    // 步骤3：批量诊断
    console.log('\n正在批量诊断...');
    const diagnoseResult = await batchDiagnose(questions, userAnswers);
    
    // 步骤4：展示诊断结果
    const summary = diagnoseResult.summary;
    console.log('\n=== 诊断报告 ===');
    console.log(`正确率: ${summary.accuracy.toFixed(1)}%`);
    console.log(`平均掌握度: ${summary.average_mastery.toFixed(1)}%`);
    console.log(`总体建议: ${summary.overall_suggestion}`);
    
    // 展示每道题的诊断
    diagnoseResult.results.forEach(result => {
      const diagnose = result.diagnose_result;
      console.log(`\n题目 ${result.question_index}: ${diagnose.correct ? '✅' : '❌'}`);
      console.log(`  掌握度: ${diagnose.mastery_score}%`);
    });
    
  } catch (error) {
    console.error('错误:', error);
  }
}

// 运行
main();
```

### 示例 4：使用 cURL 测试

```bash
# 1. 试卷识别
curl -X POST "http://localhost:8000/api/v1/paper/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"
  }' | jq '.'

# 2. 批量诊断（需要先保存识别结果到文件）
# 2.1 先识别并保存结果
curl -X POST "http://localhost:8000/api/v1/paper/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://i.ibb.co/9knYcZdV/Screen-Shot-2025-11-16-173004-542.png"
  }' > paper_result.json

# 2.2 手动编辑答案文件 diagnose_request.json
cat > diagnose_request.json << 'EOF'
{
  "questions": [
    {
      "index": 1,
      "type": "choice",
      "question": "...",
      "options": ["A...", "B...", "C...", "D..."],
      "position": []
    }
  ],
  "answers": [
    {"question_index": 1, "user_answer": "A"}
  ]
}
EOF

# 2.3 调用批量诊断
curl -X POST "http://localhost:8000/api/v1/paper/batch-diagnose" \
  -H "Content-Type: application/json" \
  -d @diagnose_request.json | jq '.'
```

## 数据格式说明

### 试卷识别响应格式

```json
{
  "paper_structure": {
    "page_id": 1,
    "page_title": "",
    "width": 2377,
    "height": 3442,
    "part_info": [
      {
        "part_title": "选择题",
        "subject_list": [...]
      }
    ],
    "figure": []
  },
  "questions": [
    {
      "index": 1,
      "type": "choice",
      "question": "下列各组数据中,表示同一时刻的是 ( )",
      "options": [
        "A.前2s末、第2s末、第3s初",
        "B.第1s末、第2s末、第3s末",
        "C.前2s末、第2s末、前3s初",
        "D.前2s初、第2s末、第3s初"
      ],
      "position": [
        [
          {"x": 170, "y": 417},
          {"x": 1162, "y": 416},
          {"x": 1161, "y": 757},
          {"x": 170, "y": 757}
        ]
      ],
      "knowledge_points": [],
      "difficulty": "medium",
      "section_title": "选择题",
      "elements": [...]
    }
  ],
  "total_questions": 10
}
```

### 批量诊断响应格式

```json
{
  "results": [
    {
      "question_index": 1,
      "question": {...},
      "diagnose_result": {
        "correct": true,
        "correct_answer": "A",
        "user_answer": "A",
        "error_type": "无",
        "analysis": "答案正确。该题考查时刻和时间间隔的概念...",
        "mastery_score": 95,
        "next_action": "继续保持，可以尝试更难的题目",
        "recommended_practice": []
      }
    }
  ],
  "summary": {
    "total_questions": 10,
    "answered_questions": 9,
    "correct_count": 7,
    "wrong_count": 2,
    "unanswered_count": 1,
    "accuracy": 77.8,
    "average_mastery": 68.5,
    "stats_by_type": {
      "choice": {
        "total": 5,
        "correct": 4,
        "wrong": 1,
        "unanswered": 0,
        "accuracy": 80.0
      },
      "fill": {
        "total": 3,
        "correct": 2,
        "wrong": 1,
        "unanswered": 0,
        "accuracy": 66.7
      }
    },
    "weak_knowledge_points": [
      {
        "knowledge": "运动学基础",
        "error_count": 2,
        "total_count": 3,
        "accuracy": 33.3,
        "recommended_practice_count": 4
      }
    ],
    "overall_suggestion": "有 1 道题目未作答，建议完成所有题目以获得更全面的诊断。正确率良好，还有提升空间。建议重点复习错题涉及的知识点。主要薄弱知识点：运动学基础。建议集中练习这些知识点。"
  }
}
```

## 错误处理

### 常见错误及处理

```python
import requests

try:
    response = requests.post(
        f"{API_BASE}/paper/recognize",
        json={"image_url": image_url}
    )
    response.raise_for_status()  # 检查 HTTP 错误
    result = response.json()
    
except requests.exceptions.HTTPError as e:
    if response.status_code == 400:
        print(f"请求参数错误: {response.json()['detail']}")
    elif response.status_code == 500:
        print(f"服务器错误: {response.json()['detail']}")
    else:
        print(f"HTTP 错误: {e}")
        
except requests.exceptions.ConnectionError:
    print("连接错误，请检查服务是否启动")
    
except requests.exceptions.Timeout:
    print("请求超时，请稍后重试")
    
except Exception as e:
    print(f"未知错误: {e}")
```

## 性能建议

1. **图片大小** - 建议压缩到 2MB 以内，保持清晰度
2. **并发控制** - 单次批量诊断建议不超过 20 题
3. **缓存机制** - 识别结果可以缓存，避免重复调用
4. **异步处理** - 对于大批量诊断，建议使用异步任务队列

## 测试脚本

运行完整测试：

```bash
# 进入后端目录
cd learning_diagnosis_backend

# 运行试卷识别测试
python test/test_paper_ocr.py

# 运行试卷识别 + 批量诊断测试（较慢）
python test/test_paper_ocr.py --with-diagnose

# 使用自定义图片测试
python test/test_paper_ocr.py --image-url "https://your-image-url.com/paper.jpg"
```

## 下一步

- 查看完整的[功能说明文档](./试卷结构化识别功能说明.md)
- 集成到前端应用
- 添加题库功能
- 实现错题本

