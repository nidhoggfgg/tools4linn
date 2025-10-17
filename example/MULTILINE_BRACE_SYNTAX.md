# 多行花括号语法

## 概述

除了传统的逗号分隔花括号语法 `{a,b,c}`，现在还支持更清晰的多行语法：

```
{
  a
  b
  c
}
```

## 为什么需要多行语法？

当需要展开的项目较多时，多行语法可以提供更好的可读性：

```python
# 传统写法 - 当项目很多时不易阅读
template = """
microservices/
  {user-service,order-service,payment-service,notification-service}/
    {src,tests,docs}/
"""

# 多行写法 - 更清晰
template = """
microservices/
  {
    user-service
    order-service
    payment-service
    notification-service
  }/
    {
      src
      tests
      docs
    }/
"""
```

## 语法规则

1. **基本格式**：花括号可以跨越多行
2. **项目分隔**：每个项目占一行
3. **空白处理**：自动去除每行前后的空白
4. **空行忽略**：花括号内的空行会被忽略
5. **兼容性**：仍然支持在同一行内使用逗号分隔

## 使用示例

### 示例 1：基本多行语法

```python
from toolkits.file.directory_creator import DirectoryCreator

creator = DirectoryCreator(base_path="./my_project")
creator.create_from_template('''
project/
  {
    frontend
    backend
    mobile
  }/
''')

# 创建的目录结构：
# project/
#   frontend/
#   backend/
#   mobile/
```

### 示例 2：嵌套多行语法

```python
creator.create_from_template('''
project/
  src/
    {
      components
      services
      utils
      models
    }/
  tests/
    {
      unit
      integration
      e2e
    }/
''')
```

### 示例 3：多行与逗号混合

你可以在同一个模板中混合使用多行和逗号语法：

```python
creator.create_from_template('''
project/
  {
    app1,app2
    app3
    app4,app5,app6
  }/
    {src,tests}/
''')

# app1 和 app2 在同一行，用逗号分隔
# app3 单独一行
# app4、app5、app6 在同一行，用逗号分隔
```

### 示例 4：与范围展开组合

多行语法可以和数字范围、字母范围等其他展开语法配合使用：

```python
creator.create_from_template('''
data/
  {
    production
    staging
    development
  }/
    year_{2023..2025}/
      quarter_{1..4}/
''')
```

### 示例 5：复杂的嵌套结构

```python
creator.create_from_template('''
microservices/
  {
    user-service
    order-service
    payment-service
    notification-service
  }/
    {
      src
      tests
      docs
    }/
      {
        models
        controllers
        services
      }/
''')

# 这将创建：
# 4个微服务 × 3个子目录 × 3个层级 = 48个叶子目录
# 加上中间目录，总共54个目录
```

## 实现原理

1. **预处理阶段**：在解析模板之前，`_merge_multiline_braces` 函数会扫描模板
2. **识别多行花括号**：检测跨越多行的花括号块
3. **合并为单行**：将多行花括号内的内容用逗号连接，转换为标准的单行花括号语法
4. **标准处理**：后续使用标准的 `_expand_braces` 函数进行展开

例如：
```
输入：
{
  a
  b
}

预处理后：
{a,b}

展开后：
['a', 'b']
```

## 注意事项

1. 多行花括号会被自动转换为逗号分隔的单行格式
2. 花括号内的空行会被忽略
3. 每行前后的空白字符会被自动去除
4. 可以在多行语法中混合使用逗号分隔

## 测试

运行 `example/test_multiline_braces.py` 查看完整的测试用例和效果演示。

