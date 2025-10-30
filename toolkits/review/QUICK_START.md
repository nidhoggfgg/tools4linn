# 文档审查功能 - 快速开始

## 5分钟快速上手

### 第一步：安装依赖

```bash
cd /Users/nidhoggnone/project/tools4linn
uv sync

# 安装系统依赖（仅首次需要）
# macOS
brew install poppler

# Ubuntu/Debian
# sudo apt-get install poppler-utils
```

### 第二步：配置API密钥

```bash
# 设置通义千问API密钥
export DASHSCOPE_API_KEY="your-api-key-here"
```

> 💡 获取API密钥: 访问 [阿里云百炼平台](https://www.aliyun.com/product/bailian)

### 第三步：准备提示词文件

创建一个 `my_prompt.txt` 文件：

```text
请分析这张图片中的信息，提取以下字段并以JSON格式返回（用```json ```包裹）：

- name: 姓名
- age: 年龄（数字）
- city: 城市
- phone: 电话

示例格式：
```json
{
  "name": "张三",
  "age": 30,
  "city": "北京",
  "phone": "13800138000"
}
```
```

### 第四步：使用功能

#### 方式1: 使用UI界面（推荐新手）

```bash
# 启动应用
uv run python main.py

# 然后：
# 1. 点击左侧 "📄 文档审查"
# 2. 选择你的文档（PDF或图片）
# 3. 选择提示词文件（或直接在界面中编辑）
# 4. 输入参考数据（JSON格式）
# 5. 点击 "开始审查"
# 6. 等待结果显示
```

#### 方式2: 使用Python代码

创建 `my_review.py`:

```python
from toolkits.review import DocumentReviewer

# 初始化
reviewer = DocumentReviewer()

# 参考数据
reference_data = {
    "name": "张三",
    "age": 30,
    "city": "北京",
    "phone": "13800138000"
}

# 审查文档
result = reviewer.review_and_compare(
    file_path="your_document.pdf",  # 改成你的文档路径
    prompt_path="my_prompt.txt",
    reference_data=reference_data
)

# 打印结果
print("提取的数据:")
print(result["extracted_data"])
print("\n差异:")
print(result["formatted_differences"])
```

运行：
```bash
uv run python my_review.py
```

## 常见场景示例

### 场景1: 身份证信息验证

**提示词 (id_card_prompt.txt):**
```text
请提取这张身份证图片中的信息，以JSON格式返回：

字段：
- name: 姓名
- id_number: 身份证号
- address: 地址
- birth_date: 出生日期

返回格式：
```json
{
  "name": "xxx",
  "id_number": "xxx",
  "address": "xxx",
  "birth_date": "xxx"
}
```
```

**Python代码:**
```python
from toolkits.review import DocumentReviewer

reviewer = DocumentReviewer()

# 数据库中的参考数据
reference = {
    "name": "张三",
    "id_number": "110101199001011234",
    "address": "北京市朝阳区xxx",
    "birth_date": "1990-01-01"
}

# 审查身份证照片
result = reviewer.review_and_compare(
    file_path="id_card.jpg",
    prompt_path="id_card_prompt.txt",
    reference_data=reference
)

# 检查是否有差异
if result["differences"]:
    print("⚠️ 发现数据不一致!")
    print(result["formatted_differences"])
else:
    print("✅ 数据验证通过!")
```

### 场景2: 表单数据核对

**提示词 (form_prompt.txt):**
```text
请提取表单中的所有字段信息，以JSON格式返回：

```json
{
  "field1": "value1",
  "field2": "value2"
}
```
```

**使用JSON文件作为参考:**
```python
import json
from toolkits.review import DocumentReviewer

reviewer = DocumentReviewer()

# 从文件加载参考数据
with open("reference.json", "r", encoding="utf-8") as f:
    reference_data = json.load(f)

# 审查表单
result = reviewer.review_and_compare(
    file_path="form.pdf",
    prompt_path="form_prompt.txt",
    reference_data=reference_data
)

# 保存结果
with open("result.json", "w", encoding="utf-8") as f:
    json.dump({
        "extracted": result["extracted_data"],
        "differences": result["differences"]
    }, f, ensure_ascii=False, indent=2)

print(f"发现 {len(result['differences'])} 处差异")
```

### 场景3: 批量文档处理

```python
from pathlib import Path
from toolkits.review import DocumentReviewer
import json

reviewer = DocumentReviewer()

# 参考数据列表
documents = [
    {"file": "doc1.pdf", "reference": {"name": "张三", "age": 30}},
    {"file": "doc2.pdf", "reference": {"name": "李四", "age": 25}},
    {"file": "doc3.pdf", "reference": {"name": "王五", "age": 35}},
]

# 批量处理
results = []
for doc in documents:
    print(f"处理: {doc['file']}")
    
    result = reviewer.review_and_compare(
        file_path=doc["file"],
        prompt_path="prompt.txt",
        reference_data=doc["reference"]
    )
    
    results.append({
        "file": doc["file"],
        "has_differences": len(result["differences"]) > 0,
        "differences": result["differences"]
    })

# 保存批量结果
with open("batch_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"完成！共处理 {len(results)} 个文档")
```

## 运行测试

测试数据比对功能：
```bash
uv run python example/test_document_reviewer.py
```

## 故障排除

### 问题1: "ModuleNotFoundError: No module named 'openai'"

**解决:**
```bash
cd /Users/nidhoggnone/project/tools4linn
uv sync
```

### 问题2: "DASHSCOPE_API_KEY 未配置"

**解决:**
```bash
export DASHSCOPE_API_KEY="your-api-key"
# 或者在代码中直接指定
reviewer = DocumentReviewer(api_key="your-api-key")
```

### 问题3: PDF转换失败

**解决:**
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# 检查安装
pdftoppm -v
```

### 问题4: "No JSON found in AI response"

**原因:** AI可能没有按照提示词要求返回JSON格式

**解决:**
1. 检查提示词是否明确要求JSON格式
2. 确保提示词中包含示例格式
3. 在提示词中强调使用 \`\`\`json 包裹
4. 尝试更详细的提示词

**优化的提示词模板:**
```text
请严格按照以下要求分析图片：

1. 提取以下字段的数据
2. 必须以JSON格式返回
3. JSON必须用```json ```包裹
4. 不要添加任何额外说明文字

字段：
- field1: 说明1
- field2: 说明2

必须严格按照此格式返回：
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

重要：只返回JSON，不要有其他内容！
```

## 下一步

- 📖 查看完整API文档: [`README.md`](README.md)
- 💡 查看更多示例: [`example/review_example.py`](../../example/review_example.py)
- 🔧 查看实现细节: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)

## 获取帮助

- 查看示例代码: `example/review_example.py`
- 运行测试脚本: `example/test_document_reviewer.py`
- 阅读详细文档: `toolkits/review/README.md`

## 小贴士

1. 💡 **提示词质量很重要**: 清晰、具体的提示词会得到更好的结果
2. 🎯 **使用示例格式**: 在提示词中提供JSON示例格式
3. 🔧 **调整DPI**: 如果图片质量不好，可以提高PDF转换的DPI
4. 📁 **自动清理**: 默认会自动清理PDF生成的临时图片
5. 🔄 **嵌套数据**: 支持复杂的嵌套JSON结构比对

开始使用吧！🚀

