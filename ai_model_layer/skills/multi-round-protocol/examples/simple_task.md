# 示例1: 简单任务（单轮完成）

## 场景

用户请求添加一个简单的打印函数。

---

## 对话流程

### 用户
```
请添加一个打印 "Hello World" 的函数到 Utils.cpp
```

### AI 响应

好的，我来添加这个函数。

```cpp
// Utils.cpp
void PrintHelloWorld()
{
    UE_LOG(LogTemp, Log, TEXT("Hello World"));
}
```

已在 Utils.cpp 中添加了 PrintHelloWorld 函数。

```yaml
---TASK_STATUS---
status: completed
reason: 成功添加 PrintHelloWorld 函数
confidence: 1.0
files_modified:
  - Source/MyProject/Utils.cpp
changes_summary: |
  - 添加了 PrintHelloWorld 函数
  - 使用 UE_LOG 输出 "Hello World"
---END_STATUS---
```

---

## 分析

### 为什么使用 COMPLETED？

- ✅ 任务简单明确
- ✅ 一次性完成
- ✅ 没有任何问题
- ✅ 信心度很高（1.0）

### 关键点

1. **状态选择正确** - 任务完成，使用 completed
2. **信心度合理** - 简单任务，信心度 1.0
3. **信息完整** - 包含修改的文件和变更说明
4. **格式规范** - 严格遵循协议格式

---

## 变体示例

### 如果需要添加头文件声明

```yaml
---TASK_STATUS---
status: completed
reason: 成功添加 PrintHelloWorld 函数及声明
confidence: 1.0
files_modified:
  - Source/MyProject/Utils.h
  - Source/MyProject/Utils.cpp
changes_summary: |
  - 在 Utils.h 中添加函数声明
  - 在 Utils.cpp 中实现函数
---END_STATUS---
```

### 如果有小问题

```yaml
---TASK_STATUS---
status: partial
reason: 添加了函数，但未添加注释
confidence: 0.8
completed:
  - 实现了 PrintHelloWorld 函数
warnings:
  - 缺少函数注释
can_proceed: true
recommended_action: 建议添加函数注释说明用途
---END_STATUS---
```

