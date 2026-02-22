# Multi-Round Protocol - 快速参考

## 🚀 基本用法

在每次响应末尾输出：

```yaml
---TASK_STATUS---
status: completed
reason: 任务完成
confidence: 0.9
---END_STATUS---
```

---

## 📋 6种状态

| 状态 | 何时使用 | 信心度 |
|------|----------|--------|
| **completed** | 任务完成，无问题 | 0.8-1.0 |
| **partial** | 完成但有警告 | 0.5-0.8 |
| **continue** | 任务太大，需继续 | - |
| **need_human** | 需要用户决策 | - |
| **error** | 遇到错误 | - |
| **waiting** | 等待外部操作 | - |

---

## ✅ 快速示例

### COMPLETED
```yaml
---TASK_STATUS---
status: completed
reason: 成功添加功能
confidence: 0.9
files_modified:
  - file1.cpp
  - file2.h
---END_STATUS---
```

### CONTINUE
```yaml
---TASK_STATUS---
status: continue
reason: 完成头文件，需继续实现
progress: 0.4
next_part: 实现 .cpp 文件
---END_STATUS---
```

### NEED_HUMAN
```yaml
---TASK_STATUS---
status: need_human
reason: 需要选择实现方案
intervention_type: decision
priority: high
question: 方案1还是方案2？
---END_STATUS---
```

### ERROR
```yaml
---TASK_STATUS---
status: error
error_type: compile
error_message: 编译错误信息
suggested_fix: 如何修复
---END_STATUS---
```

---

## 🎯 决策树

```
完成了吗？
├─ 是 → 有问题？
│  ├─ 无 → completed (0.8-1.0)
│  └─ 有 → partial (0.5-0.8)
└─ 否 → 为什么？
   ├─ 太大 → continue
   ├─ 需决策 → need_human
   ├─ 错误 → error
   └─ 等待 → waiting
```

---

## ⚠️ 关键规则

1. ✅ **始终输出状态块**
2. ✅ **诚实评估信心度**
3. ✅ **不确定时主动询问**
4. ✅ **提供详细信息**

---

**详细文档**: [SKILL.md](SKILL.md)

