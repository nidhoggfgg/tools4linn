# 花括号展开语法指南

## 概述

`DirectoryCreator` 现在支持强大的花括号展开语法，让你可以用简洁的方式快速创建大量目录。

## 语法特性

### 1. 逗号分隔列表 `{a,b,c}`

快速创建多个同级目录：

```python
from toolkits.file.directory_creator import DirectoryCreator

creator = DirectoryCreator(base_path="./my_project")
creator.create_from_template("""
project/
  src/
    {components,services,utils,models}/
  tests/
    {unit,integration,e2e}/
""")
```

创建结果：
```
project/
  src/
    components/
    services/
    utils/
    models/
  tests/
    unit/
    integration/
    e2e/
```

### 2. 数字范围 `{1..10}`

创建带编号的目录：

```python
creator.create_from_template("""
courses/
  week_{1..12}/
    day_{1..7}/
""")
```

创建：week_1 到 week_12，每周有 day_1 到 day_7

### 3. 补零数字范围 `{01..10}`

保持统一位数（自动补零）：

```python
creator.create_from_template("""
data/
  batch_{001..100}/
""")
```

创建：batch_001, batch_002, ..., batch_100

### 4. 字母范围 `{a..z}`

创建字母编号的目录：

```python
creator.create_from_template("""
sections/
  section_{A..Z}/
""")
```

创建：section_A 到 section_Z

### 5. 嵌套展开

组合使用实现笛卡尔积效果：

```python
creator.create_from_template("""
microservices/
  {user,product,order}-service/
    {src,tests}/
      {models,views,controllers}/
""")
```

创建 3 个服务 × 2 个目录 × 3 个子目录 = 每个服务都有完整的结构

### 6. 结合文件创建

```python
creator.create_from_template("""
app/
  {frontend,backend,mobile}/
    src/
      __init__.py
    tests/
      __init__.py
    README.md
""", create_files=True)
```

每个模块都会创建相同的文件结构

## 实战示例

### 示例 1：微服务架构

```python
creator.create_from_template("""
microservices/
  {user,product,order,payment,notification}-service/
    src/
      {models,views,controllers,services,middleware}/
    tests/
      {unit,integration}/
    {docs,config}/
    Dockerfile
""", create_files=True)
```

一次性创建 5 个微服务的完整目录结构！

### 示例 2：前端组件库

```python
creator.create_from_template("""
components/
  {Button,Input,Card,Modal,Table,Form}/
    {src,tests,stories}/
      index.ts
    README.md
    package.json
""", create_files=True)
```

快速搭建组件库结构

### 示例 3：日志存储（年月日结构）

```python
creator.create_from_template("""
logs/
  {2023..2025}/
    {01..12}/
      {01..31}/
""")
```

创建 3 年 × 12 月 × 31 天 = 1116 个目录！

### 示例 4：多语言项目

```python
creator.create_from_template("""
locales/
  {en,zh,ja,ko,fr,de,es}/
    {common,auth,dashboard,settings}/
""")
```

### 示例 5：数据管道

```python
creator.create_from_template("""
data_pipeline/
  {raw,processed,validated,archived}/
    year_{2020..2024}/
      month_{01..12}/
""")
```

### 示例 6：测试环境

```python
creator.create_from_template("""
environments/
  {dev,staging,prod}/
    {configs,secrets,backups}/
    docker-compose.yml
    .env
""", create_files=True)
```

### 示例 7：API 版本管理

```python
creator.create_from_template("""
api/
  v{1..5}/
    {users,posts,comments,auth,media}/
      {controllers,models,validators}/
""")
```

## 性能说明

- 支持大规模目录创建（测试过 1000+ 目录）
- 展开过程是递归的，会自动处理所有嵌套层级
- 使用去重机制避免重复创建

## 禁用花括号展开

如果你的目录名本身包含花括号，可以禁用展开：

```python
creator.create_from_template("""
project/
  {special-name}/
""", expand_braces=False)
```

## 组合使用其他语法

花括号展开可以与其他模板语法特性组合：

- ✅ 注释（# 开头的行）
- ✅ 文件创建（带扩展名 + `create_files=True`）
- ✅ 强制目录标记（末尾 /）
- ✅ 任意缩进（空格或制表符）

## 更多示例

查看 `example/test_brace_expansion.py` 获取完整的可运行示例。

