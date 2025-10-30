# Review Module

文档审查模块，用于从图片或PDF中提取数据并与参考数据进行对比。

## 功能特性

- ✅ 支持PDF自动转图片
- ✅ 支持多种图片格式（PNG, JPG, JPEG, GIF, WebP）
- ✅ 使用AI视觉模型提取结构化数据
- ✅ 自动解析AI返回的JSON数据
- ✅ 智能比对两组数据的差异
- ✅ 支持嵌套字段比对
- ✅ 自动清理临时文件

## 安装依赖

```bash
# 使用 uv
uv sync

# 或使用 pip
pip install openai pdf2image
```

**注意**: `pdf2image` 需要系统安装 `poppler`:

- **macOS**: `brew install poppler`
- **Ubuntu/Debian**: `apt-get install poppler-utils`
- **Windows**: 下载并配置 poppler，参考 [pdf2image文档](https://github.com/Belval/pdf2image)

## 快速开始

### 1. 配置 API

在应用的设置页面配置 API Key 和 Base URL，或使用配置管理器：

```python
from toolkits.utils.config import get_config_manager

config = get_config_manager()
config.set_api_key("your-api-key")
config.set_api_base_url("https://your-api-endpoint.com")
```

### 2. 准备提示词文件 (prompt.txt)

```text
请仔细分析这张图片中的信息，并提取以下字段的数据。
请以JSON格式返回结果，确保JSON被```json ```包裹。

需要提取的字段：
- name: 姓名
- age: 年龄
- city: 城市
- phone: 电话号码

返回格式示例：
```json
{
  "name": "张三",
  "age": 30,
  "city": "北京",
  "phone": "13800138000"
}
```
```

### 3. 使用示例

```python
from toolkits.review import DocumentReviewer
from toolkits.ai.client import AIChatClient
from toolkits.utils.config import get_config_manager

# 获取配置
config = get_config_manager()
api_key = config.get_api_key()
base_url = config.get_api_base_url()

# 初始化 AI 客户端
ai_client = AIChatClient(api_key=api_key, base_url=base_url)

# 初始化审查器
reviewer = DocumentReviewer(
    ai_client=ai_client,
    model="qwen-vl-max-latest",  # 视觉模型
    pdf_dpi=300  # PDF转图片的DPI
)

# 准备参考数据
reference_data = {
    "name": "张三",
    "age": 30,
    "city": "北京",
    "phone": "13800138000"
}

# 审查并对比
result = reviewer.review_and_compare(
    file_path="document.pdf",  # 支持 PDF 或图片
    prompt_path="prompt.txt",   # 提示词文件
    reference_data=reference_data,  # 参考数据
    cleanup_images=True  # 自动清理PDF生成的临时图片
)

# 查看结果
print("提取的数据:", result["extracted_data"])
print("差异列表:", result["differences"])
print("格式化的差异:", result["formatted_differences"])
```

## API 文档

### DocumentReviewer

主要的文档审查类。

#### 初始化参数

- `ai_client` (AIChatClient, required): AI客户端实例（必填）
- `model` (str): 使用的AI视觉模型，默认 "qwen-vl-max-latest"
- `pdf_dpi` (int): PDF转图片的DPI，默认 300

#### review_and_compare()

审查文档并与参考数据对比。

**参数:**
- `file_path` (str | Path): 图片或PDF文件路径
- `prompt_path` (str | Path): 提示词文件路径
- `reference_data` (dict): 参考数据字典
- `cleanup_images` (bool): 是否清理生成的临时图片，默认 True

**返回:**
```python
{
    "extracted_data": dict,  # 从文档中提取的数据
    "differences": list,     # 差异列表（详细）
    "formatted_differences": str  # 格式化的差异描述
}
```

### DataComparator

数据比对工具类。

#### compare()

比对两个字典并返回差异。

**参数:**
- `data1` (dict): 第一个数据字典（如AI提取的数据）
- `data2` (dict): 第二个数据字典（如参考数据）

**返回:** 差异列表

```python
[
    {
        "field": "字段名",
        "value1": "数据1的值",
        "value2": "数据2的值",
        "status": "different" | "missing_in_data1" | "missing_in_data2"
    }
]
```

#### format_differences()

将差异列表格式化为可读字符串。

### PDFConverter

PDF转图片工具类。

#### convert_to_images()

将PDF转换为图片。

**参数:**
- `pdf_path` (str | Path): PDF文件路径
- `output_folder` (str | Path, optional): 输出文件夹，默认在PDF同目录
- `fmt` (str): 图片格式，默认 "png"

**返回:** 生成的图片路径列表

## 差异状态说明

- `different`: 字段在两个数据中都存在但值不同
- `missing_in_data1`: 字段只在第二个数据中存在（第一个数据缺失）
- `missing_in_data2`: 字段只在第一个数据中存在（第二个数据缺失）

## 高级用法

### 处理嵌套数据

比对器支持嵌套字典的比对：

```python
data1 = {
    "user": {
        "name": "张三",
        "address": {
            "city": "北京",
            "district": "朝阳区"
        }
    }
}

data2 = {
    "user": {
        "name": "李四",
        "address": {
            "city": "北京",
            "district": "海淀区"
        }
    }
}

differences = DataComparator.compare(data1, data2)
# 将显示: user.name 和 user.address.district 的差异
```

### 使用JSON文件作为参考数据

```python
import json

# 加载参考数据
with open("reference.json", "r", encoding="utf-8") as f:
    reference_data = json.load(f)

# 进行审查
result = reviewer.review_and_compare(
    file_path="document.pdf",
    prompt_path="prompt.txt",
    reference_data=reference_data
)

# 保存结果
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(result["differences"], f, ensure_ascii=False, indent=2)
```

### 自定义AI客户端

```python
from toolkits.ai.client import AIChatClient
from toolkits.utils.config import get_config_manager

# 方式1: 从配置管理器获取
config = get_config_manager()
ai_client = AIChatClient(
    api_key=config.get_api_key(),
    base_url=config.get_api_base_url()
)

# 方式2: 直接提供配置
ai_client = AIChatClient(
    api_key="your-key",
    base_url="https://your-api-endpoint.com"
)

reviewer = DocumentReviewer(ai_client=ai_client)
```

## 注意事项

1. **API配置**: 使用前需要配置 API Key 和 Base URL，可在应用设置页面或使用配置管理器
2. **图片质量**: PDF转换使用300 DPI，可根据需要调整
3. **临时文件**: PDF转图片会生成临时文件，建议启用 `cleanup_images=True`
4. **多页PDF**: 当前版本使用第一页数据，后续可扩展支持多页合并逻辑
5. **JSON格式**: 确保提示词要求AI返回被 \`\`\`json 包裹的JSON格式

## 示例文件

更多示例请参考: `example/review_example.py`

## 错误处理

```python
try:
    result = reviewer.review_and_compare(
        file_path="document.pdf",
        prompt_path="prompt.txt",
        reference_data=reference_data
    )
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except ValueError as e:
    print(f"数据解析错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 许可证

与主项目相同

