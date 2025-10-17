# Tools4Linn

一套实用的 Python 工具集合。

## 功能模块

### 📁 目录创建器 (Directory Creator)

强大的多层目录批量创建工具，支持多种灵活的语法。

#### 🎨 最新特性：可视化树形UI（低代码方式）

全新的树状模式UI，无需手动输入文本，通过可视化操作构建目录结构：

- 🖱️ **可视化操作**：点击按钮添加、删除、重命名节点
- 📊 **树形展示**：直观显示完整的目录层级结构
- 🔄 **灵活调整**：支持上移、下移调整节点顺序
- 📁 **文件支持**：同时支持创建文件夹和文件
- 💡 **零学习成本**：类似文件管理器的操作体验
- 🎯 **延迟花括号展开**：输入 `{a,b,c}` 显示为单个节点，可继续添加子目录，创建时自动展开（适合批量创建相同结构）
- ⚡ **批量添加模式**：输入纯列表（每行一个），快速创建多个独立节点

详见：[树状模式使用指南](example/ui_tree_mode_example.md) | [延迟花括号展开指南](example/DELAYED_BRACE_EXPANSION_GUIDE.md)

#### ✨ 特性：花括号展开语法

类似 bash 的花括号展开语法，让你能用极简的方式创建大量目录！

```python
from toolkits.file.directory_creator import DirectoryCreator

creator = DirectoryCreator(base_path="./my_project")

# 快速创建多个同级目录
creator.create_from_template("""
project/
  src/
    {components,services,utils}/
  tests/
    {unit,integration,e2e}/
""")

# 数字范围展开 - 创建 100 个批次目录
creator.create_from_template("""
data/
  batch_{001..100}/
    {raw,processed}/
""")

# 嵌套展开 - 为多个微服务创建相同结构
creator.create_from_template("""
microservices/
  {user,product,order}-service/
    {src,tests}/
      {models,views,controllers}/
""")

# 日期结构 - 创建年月日目录
creator.create_from_template("""
logs/
  {2023..2025}/
    {01..12}/
      {01..31}/
""")
```

**支持的展开模式：**
- `{a,b,c}` - 逗号分隔列表
- `{1..10}` - 数字范围
- `{01..10}` - 补零数字范围
- `{a..z}` - 字母范围
- 完全支持嵌套展开

**实际案例：**
- ✅ 一次创建 1000+ 目录
- ✅ 微服务架构快速搭建
- ✅ 日志目录结构
- ✅ 多语言项目
- ✅ API 版本管理

查看 [`example/BRACE_EXPANSION_GUIDE.md`](example/BRACE_EXPANSION_GUIDE.md) 获取完整使用指南。

#### 其他语法支持

**1. 列表语法（最简单）**
```python
creator.create_from_list([
    "src/components",
    "src/utils",
    "tests/unit"
])
```

**2. 字典语法（最直观）**
```python
creator.create_from_dict({
    "src": {
        "components": ["Button", "Input"],
        "utils": None
    },
    "tests": ["unit", "integration"]
})
```

**3. 模板语法（可视化）**
```python
creator.create_from_template("""
project/
  src/
    components/
    utils/
  tests/
    unit/
""")
```

### 📊 Excel 合并工具 (Excel Merger)

位于 `toolkits/excel/merge_excel.py`

### ⏰ 时间生成器 (Time Generator)

位于 `toolkits/time/time_generator.py`

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd tools4linn

# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

## 使用方式

### 命令行方式

```bash
python main.py
```

### 作为库使用

```python
from toolkits.file.directory_creator import DirectoryCreator

# 创建实例
creator = DirectoryCreator(base_path="./output")

# 使用任意语法创建目录
creator.create_from_template("""
my_project/
  {src,tests,docs}/
""")

# 查看创建的目录
creator.print_tree()
```

## 示例

查看 `example/` 目录获取更多示例：

- `examples_directory_creator.py` - 基础用法示例
- `test_brace_expansion.py` - 花括号展开语法示例
- `BRACE_EXPANSION_GUIDE.md` - 完整的语法指南

运行示例：
```bash
python example/test_brace_expansion.py
```

## 项目结构

```
tools4linn/
├── toolkits/           # 工具包模块
│   ├── file/          # 文件操作工具
│   ├── excel/         # Excel 处理工具
│   ├── time/          # 时间处理工具
│   └── utils/         # 通用工具
├── ui/                # UI 界面（基于 PySide6）
├── example/           # 示例代码
└── main.py           # 主入口
```

## 开发

使用 `uv` 作为包管理器：

```bash
# 添加依赖
uv add <package-name>

# 运行脚本
uv run python main.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

