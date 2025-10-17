# 延迟花括号展开 - 快速入门

## 🎯 60秒快速理解

### 核心概念

输入 `{a,b,c}` → 树形视图中显示为**一个节点** → 可以继续添加子目录 → 创建时自动展开

---

## 🚀 实战演练

### 场景：创建3个微服务，每个都有相同的src和tests目录

#### 传统方式（需要重复9次操作）：
```
1. 添加 user-service
2. 在 user-service 下添加 src
3. 在 user-service 下添加 tests
4. 添加 order-service
5. 在 order-service 下添加 src
6. 在 order-service 下添加 tests
7. 添加 product-service
8. 在 product-service 下添加 src
9. 在 product-service 下添加 tests
```

#### 新方式（只需3次操作）：
```
1. 添加文件夹，输入: {user-service,order-service,product-service}
2. 选择这个节点，添加 src
3. 选择这个节点，添加 tests
```

---

## 📝 实际操作步骤

### 步骤1：添加花括号节点

1. 打开应用，选择"树状模式"
2. 选择"根目录"节点
3. 点击"➕ 添加文件夹"按钮
4. 在弹出的对话框中输入：
   ```
   {user-service,order-service,product-service}
   ```
   或者多行格式：
   ```
   {
   user-service
   order-service
   product-service
   }
   ```
5. 点击"确定"

**结果：** 看到提示"已添加花括号节点: {user-service,order-service,product-service}，创建时将自动展开"

### 步骤2：添加统一的子结构

6. 选择刚才添加的 `{user-service,order-service,product-service}` 节点
7. 点击"➕ 添加文件夹"，输入 `src`
8. 再次选择 `{user-service,order-service,product-service}` 节点
9. 点击"➕ 添加文件夹"，输入 `tests`
10. 再次选择 `{user-service,order-service,product-service}` 节点
11. 点击"📄 添加文件"，输入 `README.md`

**树形视图显示：**
```
📁 根目录
  📁 {user-service,order-service,product-service}
    📁 src
    📁 tests
    📄 README.md
```

### 步骤3：创建

12. 点击"✨ 开始创建"按钮
13. 选择保存位置
14. 确认创建

**最终结果：**
```
📁 user-service/
  📁 src/
  📁 tests/
  📄 README.md
📁 order-service/
  📁 src/
  📁 tests/
  📄 README.md
📁 product-service/
  📁 src/
  📁 tests/
  📄 README.md
```

---

## 💡 关键点

### 1. 花括号 = 单个节点
- ✅ 输入: `{a,b,c}`
- ✅ 显示: 一个节点 `{a,b,c}`
- ✅ 创建: 三个目录 `a/`, `b/`, `c/`

### 2. 无花括号 = 多个节点
- ✅ 输入: `a\nb\nc` (每行一个)
- ✅ 显示: 三个节点 `a`, `b`, `c`
- ✅ 创建: 三个目录 `a/`, `b/`, `c/`

### 3. 何时用花括号？
需要为多个目录创建**相同的子结构**时

### 4. 何时不用花括号？
每个目录的子结构**不同**时

---

## 🎨 更多示例

### 示例1：创建12周课程

**输入：**
```
week_{1..12}
```

**在此节点下添加：**
- materials （文件夹）
- homework （文件夹）
- notes.md （文件）

**创建结果：** 12个周次目录，每个都包含 materials/, homework/, notes.md

---

### 示例2：多语言目录

**输入：**
```
{en,zh,ja,ko}
```

**在此节点下添加：**
- pages （文件夹）
- components （文件夹）

**创建结果：** 4个语言目录，每个都包含 pages/ 和 components/

---

### 示例3：多环境配置

**输入：**
```
{dev,staging,prod}
```

**在此节点下添加：**
- config.json （文件）
- .env （文件）

**创建结果：** 3个环境目录，每个都包含 config.json 和 .env

---

## ⚡ 常用花括号语法

```bash
{a,b,c}              # 3个目录
{1..10}              # 10个目录 (1到10)
{01..31}             # 31个目录 (01到31，补零)
{A..Z}               # 26个目录 (A到Z)
week_{1..12}         # week_1 到 week_12
{main,test}.py       # main.py 和 test.py
```

---

## 🔧 故障排查

### Q: 输入 `{a,b,c}` 后显示了3个节点？
A: 可能输入格式有误，确保花括号没有被分行（或使用多行格式）

### Q: 创建后只有一个目录叫 `{a,b,c}`？
A: 检查是否正确调用了创建功能，花括号应该会自动展开

### Q: 想创建3个独立的不同结构目录？
A: 不要用花括号，直接输入：
```
a
b
c
```

---

## 📚 下一步

- 阅读 [完整的延迟展开指南](./DELAYED_BRACE_EXPANSION_GUIDE.md)
- 查看 [花括号语法详解](./BRACE_EXPANSION_GUIDE.md)
- 尝试更多 [实战示例](./DELAYED_BRACE_EXPANSION_GUIDE.md#实战示例)

---

**开始使用吧！** 🎉

运行：`python main.py` → 选择"目录创建器" → 选择"树状模式" → 开始创建！

