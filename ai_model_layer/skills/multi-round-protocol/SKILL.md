# Multi-Round Protocol Skill

AI 多轮对话任务执行的标准化协议。

## 📋 Skill 信息

- **名称**: Multi-Round Protocol
- **版本**: 2.0.0
- **用途**: 标准化 AI 处理复杂任务的多轮对话流程

---

## 🎯 Skill 目标

当 AI 需要处理复杂任务时，使用此协议可以：

1. ✅ 自动追踪任务进度
2. ✅ 明确何时需要人工介入
3. ✅ 标准化错误处理
4. ✅ 支持任务分步执行
5. ✅ 提供可验证的完成状态

---

## 🚀 快速开始

### 基本用法

在每次响应的**末尾**输出状态块：

```yaml
---TASK_STATUS---
status: completed
reason: 任务已完成
confidence: 0.9
---END_STATUS---
```

### 6种状态类型

| 状态 | 用途 | 何时使用 |
|------|------|----------|
| **completed** | 任务完成 | 所有工作已完成，可验证 |
| **continue** | 需要继续 | 任务太大，需要分步执行 |
| **need_human** | 需要介入 | 需要用户决策或许可 |
| **error** | 遇到错误 | 发生错误需要处理 |
| **waiting** | 等待中 | 等待外部操作完成 |
| **partial** | 部分完成 | 完成但有警告 |

---

## 📚 状态详解

### 1. COMPLETED - 任务完成

**用于**: 任务已完成，可以进行验证

```yaml
---TASK_STATUS---
status: completed
reason: 成功添加生命恢复能力系统
confidence: 0.9
files_modified:
  - Source/MyProject/Characters/MyCharacter.h
  - Source/MyProject/Characters/MyCharacter.cpp
changes_summary: |
  - 添加了 HealthRegenComponent
  - 实现了每秒恢复逻辑
  - 添加了配置参数
---END_STATUS---
```

**字段说明**:
- `status`: 必须是 `completed`
- `reason`: 简要说明完成了什么
- `confidence`: 0.8-1.0（低于0.8应该用 partial）
- `files_modified`: 修改的文件列表
- `changes_summary`: 详细的变更说明

**何时使用**:
- ✅ 所有代码已编写
- ✅ 所有文件已修改
- ✅ 没有已知问题
- ✅ 可以进行测试验证

---

### 2. CONTINUE - 需要继续

**用于**: 任务太大，需要在下一轮继续

```yaml
---TASK_STATUS---
status: continue
reason: 完成了头文件定义，需要继续实现 .cpp 文件
progress: 0.4
completed_parts:
  - 创建头文件
  - 定义类结构
next_part: 实现 .cpp 文件中的方法
estimated_rounds: 2
---END_STATUS---
```

**字段说明**:
- `progress`: 0.0-1.0 的进度
- `completed_parts`: 已完成的部分
- `next_part`: 下一步要做什么
- `estimated_rounds`: 预计还需要几轮

**何时使用**:
- ✅ 响应长度接近限制
- ✅ 任务自然分为多个阶段
- ✅ 需要分步验证
- ✅ 避免一次性输出过多代码

---

### 3. NEED_HUMAN - 需要人工介入

**用于**: 需要用户决策、许可或澄清

```yaml
---TASK_STATUS---
status: need_human
reason: 需要确认是否修改现有的 Health 系统
intervention_type: decision
priority: high
question: |
  发现项目中已有 HealthComponent，有两个选择：
  1. 扩展现有 HealthComponent 添加恢复功能
  2. 创建新的 HealthRegenComponent
  请问您希望采用哪种方案？
options:
  - extend_existing: 扩展现有组件（推荐）
  - create_new: 创建新组件
---END_STATUS---
```

**字段说明**:
- `intervention_type`: 
  - `permission` - 需要许可（如删除文件）
  - `decision` - 需要决策（如选择方案）
  - `clarification` - 需要澄清（如需求不明确）
- `priority`: `high` | `medium` | `low`
- `question`: 具体的问题
- `options`: 可选的选项

**何时使用**:
- ✅ 需求不明确
- ✅ 有多种实现方案
- ✅ 需要修改关键文件
- ✅ 发现潜在风险

---

### 4. ERROR - 遇到错误

**用于**: 遇到错误需要处理

```yaml
---TASK_STATUS---
status: error
error_type: compile
error_message: |
  MyCharacter.cpp(45): error C2065: 'HealthRegenRate' : undeclared identifier
error_location:
  file: Source/MyProject/Characters/MyCharacter.cpp
  line: 45
root_cause: 忘记在头文件中声明 HealthRegenRate 变量
suggested_fix: 在 MyCharacter.h 中添加 float HealthRegenRate; 声明
can_auto_fix: true
---END_STATUS---
```

**字段说明**:
- `error_type`: 
  - `syntax` - 语法错误
  - `compile` - 编译错误
  - `runtime` - 运行时错误
  - `logic` - 逻辑错误
- `error_message`: 实际的错误信息
- `error_location`: 错误位置
- `root_cause`: 根本原因
- `suggested_fix`: 修复建议
- `can_auto_fix`: 是否可以自动修复

**何时使用**:
- ✅ 编译失败
- ✅ 测试失败
- ✅ 发现逻辑错误
- ✅ 遇到技术限制

---

### 5. WAITING - 等待中

**用于**: 等待外部操作完成

```yaml
---TASK_STATUS---
status: waiting
waiting_for: compile_result
reason: 等待编译结果以验证代码正确性
timeout: 300
next_action: 根据编译结果决定下一步
fallback_plan: 如果编译失败，将分析错误并修复
---END_STATUS---
```

**字段说明**:
- `waiting_for`:
  - `compile_result` - 编译结果
  - `test_result` - 测试结果
  - `user_input` - 用户输入
  - `external_tool` - 外部工具
- `timeout`: 超时时间（秒）
- `next_action`: 收到结果后的下一步
- `fallback_plan`: 超时或失败的备选方案

**何时使用**:
- ✅ 需要编译验证
- ✅ 需要运行测试
- ✅ 等待用户提供信息
- ✅ 依赖外部工具

---

### 6. PARTIAL - 部分完成

**用于**: 任务部分完成，但有警告或非关键问题

```yaml
---TASK_STATUS---
status: partial
reason: 核心功能已实现，但缺少错误处理
confidence: 0.7
completed:
  - 实现了基础的生命恢复逻辑
  - 添加了配置参数
  - 创建了必要的文件
warnings:
  - 缺少空指针检查
  - 未处理恢复速率为负数的情况
  - 缺少单元测试
can_proceed: true
recommended_action: 建议添加错误处理后再部署
---END_STATUS---
```

**字段说明**:
- `confidence`: 0.5-0.8（低于0.5应该用 error）
- `completed`: 已完成的项目
- `warnings`: 警告列表
- `can_proceed`: 是否可以继续
- `recommended_action`: 推荐的后续操作

**何时使用**:
- ✅ 核心功能完成但有小问题
- ✅ 缺少非关键功能
- ✅ 有改进空间
- ✅ 需要后续优化

---

## 🎯 使用场景

### 场景 1: 简单任务（单轮完成）

```yaml
用户: 添加一个打印 Hello World 的函数

AI: [实现代码]

---TASK_STATUS---
status: completed
reason: 成功添加 PrintHelloWorld 函数
confidence: 1.0
files_modified:
  - Source/Utils.cpp
---END_STATUS---
```

---

### 场景 2: 复杂任务（多轮执行）

```yaml
用户: 实现一个完整的库存系统

AI 第1轮: [创建头文件和基础结构]
---TASK_STATUS---
status: continue
reason: 完成了头文件定义和基础结构
progress: 0.3
next_part: 实现库存管理逻辑
---END_STATUS---

AI 第2轮: [实现核心逻辑]
---TASK_STATUS---
status: continue
reason: 完成了核心逻辑实现
progress: 0.6
next_part: 添加 UI 界面
---END_STATUS---

AI 第3轮: [添加 UI]
---TASK_STATUS---
status: completed
reason: 库存系统完整实现
confidence: 0.9
---END_STATUS---
```

---

### 场景 3: 需要决策

```yaml
用户: 优化角色移动系统

AI: [分析现有代码]

发现两种优化方案...

---TASK_STATUS---
status: need_human
reason: 需要选择优化方案
intervention_type: decision
priority: medium
question: |
  方案1: 使用 Character Movement Component（标准方案）
  方案2: 自定义移动逻辑（更灵活）
  请问选择哪个方案？
---END_STATUS---
```

---

### 场景 4: 遇到错误

```yaml
用户: 编译项目

AI: [尝试编译]

---TASK_STATUS---
status: error
error_type: compile
error_message: "缺少 CoreMinimal.h"
suggested_fix: 在文件开头添加 #include "CoreMinimal.h"
can_auto_fix: true
---END_STATUS---

用户: 修复它

AI: [修复错误]

---TASK_STATUS---
status: completed
reason: 已修复编译错误
confidence: 0.95
---END_STATUS---
```

---

## 📋 最佳实践

### DO ✅

1. **始终输出状态块**
   ```yaml
   # 即使是简单任务也要输出
   ---TASK_STATUS---
   status: completed
   reason: 任务完成
   confidence: 1.0
   ---END_STATUS---
   ```

2. **诚实评估信心度**
   ```yaml
   # 不确定时降低信心度
   confidence: 0.7  # 而不是虚高的 0.95
   ```

3. **提供详细信息**
   ```yaml
   # 包含足够的上下文
   files_modified:
     - path/to/file1.cpp
     - path/to/file2.h
   changes_summary: |
     详细说明做了什么
   ```

4. **主动询问**
   ```yaml
   # 不确定时使用 need_human
   status: need_human
   intervention_type: clarification
   ```

### DON'T ❌

1. **不要忘记状态块**
   ```yaml
   # ❌ 错误：没有输出状态
   任务完成了。
   
   # ✅ 正确：输出状态块
   任务完成了。
   ---TASK_STATUS---
   status: completed
   ---END_STATUS---
   ```

2. **不要虚报信心度**
   ```yaml
   # ❌ 错误：不确定但声称高信心
   confidence: 0.95  # 实际只有 70% 把握
   
   # ✅ 正确：诚实评估
   confidence: 0.7
   ```

3. **不要缺少关键信息**
   ```yaml
   # ❌ 错误：信息不足
   status: error
   error_message: "出错了"
   
   # ✅ 正确：详细信息
   status: error
   error_type: compile
   error_message: "具体的错误信息"
   suggested_fix: "如何修复"
   ```

---

## 🔍 状态选择指南

### 决策树

```
任务完成了吗？
├─ 是 → 有问题吗？
│  ├─ 无问题 → completed (confidence: 0.8-1.0)
│  └─ 有警告 → partial (confidence: 0.5-0.8)
└─ 否 → 为什么没完成？
   ├─ 任务太大 → continue
   ├─ 需要决策 → need_human
   ├─ 遇到错误 → error
   └─ 等待结果 → waiting
```

### 信心度指南

| 信心度 | 含义 | 状态 |
|--------|------|------|
| 0.9-1.0 | 非常确定，几乎没有问题 | completed |
| 0.8-0.9 | 确定，可能有小问题 | completed |
| 0.7-0.8 | 基本完成，有一些问题 | partial |
| 0.5-0.7 | 部分完成，有明显问题 | partial |
| < 0.5 | 有严重问题 | error |

---

## 📊 协议优势

### 对比传统方式

**传统方式**:
```
AI: 我完成了任务。
用户: 真的吗？有没有问题？
AI: 可能有一些小问题...
用户: 什么问题？
AI: [解释问题]
```

**使用协议**:
```yaml
AI: [完成工作]

---TASK_STATUS---
status: partial
confidence: 0.75
completed: [列表]
warnings: [列表]
---END_STATUS---
```

### 好处

1. ✅ **标准化** - 统一的状态格式
2. ✅ **可追踪** - 明确的进度信息
3. ✅ **可自动化** - 机器可解析
4. ✅ **透明** - 清晰的信心度
5. ✅ **高效** - 减少来回沟通

---

## 🎓 总结

### 核心要点

1. **6种状态** - completed, continue, need_human, error, waiting, partial
2. **始终输出** - 每次响应末尾必须包含状态块
3. **诚实评估** - 真实反映信心度和问题
4. **详细信息** - 提供足够的上下文
5. **主动沟通** - 不确定时主动询问

### 记住

- ✅ 状态块是**必须的**，不是可选的
- ✅ 信心度要**诚实**，不要虚报
- ✅ 不确定时**主动询问**
- ✅ 提供**详细信息**便于追踪

---

**使用此协议，让 AI 任务执行更加标准化、可追踪、可靠！** 🎉
