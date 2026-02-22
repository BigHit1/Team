# Multi-Round Protocol Skill - 使用指南

## 📦 Skill 结构

```
multi-round-protocol/
├── README.md                    # Skill 概述
├── QUICKREF.md                  # 快速参考卡片（1页）
├── SKILL.md                     # 完整协议文档
├── USAGE.md                     # 使用指南（本文件）
├── skill.json                   # Skill 元数据
├── examples/                    # 实际场景示例
│   ├── simple_task.md          # 简单任务示例
│   ├── complex_task.md         # 复杂任务示例
│   ├── error_handling.md       # 错误处理示例
│   └── decision_making.md      # 决策场景示例
└── templates/                   # 可复用模板
    └── status_templates.yaml   # 所有状态模板
```

---

## 🚀 如何使用此 Skill

### 1. 快速入门（5分钟）

阅读 `QUICKREF.md` 获取：
- 基本用法
- 6种状态速查
- 快速示例
- 决策树

### 2. 深入学习（30分钟）

阅读 `SKILL.md` 了解：
- 每种状态的详细说明
- 使用场景和示例
- 最佳实践
- 状态选择指南

### 3. 实践应用

#### 方式1: 查看示例

- `examples/simple_task.md` - 学习单轮任务
- `examples/complex_task.md` - 学习多轮任务
- `examples/error_handling.md` - 学习错误处理
- `examples/decision_making.md` - 学习决策场景

#### 方式2: 使用模板

打开 `templates/status_templates.yaml`，复制相应的模板：
- COMPLETED 模板（基础版/完整版）
- CONTINUE 模板
- NEED_HUMAN 模板（决策/许可/澄清）
- ERROR 模板（编译/逻辑/运行时）
- WAITING 模板
- PARTIAL 模板

---

## 📋 使用场景

### 场景1: AI 执行简单任务

**适用**: 单次响应可完成的任务

**流程**:
```
用户请求 → AI 执行 → 输出 completed 状态
```

**参考**: `examples/simple_task.md`

---

### 场景2: AI 执行复杂任务

**适用**: 需要多轮对话的大型任务

**流程**:
```
用户请求 → AI 第1轮 (continue) 
         → AI 第2轮 (continue)
         → AI 第3轮 (completed)
```

**参考**: `examples/complex_task.md`

---

### 场景3: 遇到错误需要修复

**适用**: 编译错误、运行时错误等

**流程**:
```
AI 实现 (waiting) → 收到错误 (error) 
                  → AI 修复 (waiting)
                  → 验证成功 (completed)
```

**参考**: `examples/error_handling.md`

---

### 场景4: 需要用户决策

**适用**: 多种方案、需要许可、需求不明确

**流程**:
```
AI 分析 (need_human) → 用户选择 
                     → AI 继续执行 (completed)
```

**参考**: `examples/decision_making.md`

---

## 🎯 状态选择指南

### 快速决策树

```
任务完成了吗？
├─ 是 → 有问题吗？
│  ├─ 无 → completed (0.8-1.0)
│  └─ 有 → partial (0.5-0.8)
└─ 否 → 为什么？
   ├─ 太大 → continue
   ├─ 需决策 → need_human
   ├─ 错误 → error
   └─ 等待 → waiting
```

### 详细选择表

| 情况 | 状态 | 信心度 |
|------|------|--------|
| 任务完成，无问题 | completed | 0.8-1.0 |
| 任务完成，有小问题 | partial | 0.5-0.8 |
| 任务太大，需分步 | continue | - |
| 需要用户决策 | need_human | - |
| 需要用户许可 | need_human | - |
| 需求不明确 | need_human | - |
| 遇到编译错误 | error | - |
| 遇到逻辑错误 | error | - |
| 等待编译结果 | waiting | - |
| 等待测试结果 | waiting | - |

---

## 💡 最佳实践

### 对于 AI

#### DO ✅

1. **始终输出状态块**
   ```yaml
   # 即使是最简单的任务
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

#### DON'T ❌

1. **不要忘记状态块**
2. **不要虚报信心度**
3. **不要缺少关键信息**
4. **不要猜测用户意图**

---

### 对于用户

#### 如何响应不同状态

**completed**:
- 验证结果
- 测试功能
- 如有问题，提出修改

**continue**:
- 回复 "继续" 让 AI 继续
- 或者提出调整建议

**need_human**:
- 回答问题
- 做出选择
- 提供更多信息

**error**:
- 回复 "修复它" 让 AI 修复
- 或者提供额外信息

**waiting**:
- 提供等待的结果
- 如编译输出、测试结果

**partial**:
- 决定是否接受
- 或要求完善

---

## 🔍 常见问题

### Q1: 什么时候用 completed vs partial？

**A**: 看信心度和问题严重性

- **completed**: 信心度 ≥ 0.8，无问题或只有微小问题
- **partial**: 信心度 0.5-0.8，有明显问题但不影响核心功能

### Q2: 什么时候用 error vs need_human？

**A**: 看是否可以自动修复

- **error**: 明确的错误，AI 知道如何修复
- **need_human**: 需要用户决策才能继续

### Q3: 任务很大，应该一次完成还是分步？

**A**: 建议分步（使用 continue）

**优点**:
- 每步可以验证
- 避免响应过长
- 便于调整方向

**何时分步**:
- 响应长度接近限制
- 任务自然分为多个阶段
- 需要中途验证

### Q4: 信心度应该如何评估？

**A**: 基于以下因素

| 信心度 | 含义 |
|--------|------|
| 1.0 | 100%确定，简单任务 |
| 0.9-0.95 | 非常确定，经过验证 |
| 0.8-0.9 | 确定，可能有小问题 |
| 0.7-0.8 | 基本完成，有一些问题 |
| 0.5-0.7 | 部分完成，有明显问题 |
| < 0.5 | 有严重问题，应该用 error |

---

## 📊 协议优势

### 传统方式 vs 使用协议

**传统方式**:
```
AI: 我完成了任务。
用户: 真的吗？有没有问题？
AI: 可能有一些小问题...
用户: 什么问题？
AI: [解释问题]
用户: 那信心度多少？
AI: 大概70%吧...
```

**使用协议**:
```yaml
AI: [完成工作]

---TASK_STATUS---
status: partial
reason: 核心功能完成，但缺少错误处理
confidence: 0.7
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

## 🎓 学习路径

### 初级（15分钟）
- [ ] 阅读 `README.md` 和 `QUICKREF.md`
- [ ] 理解 6 种状态类型
- [ ] 查看 `examples/simple_task.md`
- [ ] 在简单任务中使用协议

### 中级（30分钟）
- [ ] 阅读完整的 `SKILL.md`
- [ ] 查看所有示例文件
- [ ] 学习使用模板
- [ ] 在复杂任务中使用协议

### 高级（1小时）
- [ ] 深入理解每种状态的使用场景
- [ ] 学习信心度评估
- [ ] 掌握错误处理流程
- [ ] 能够处理各种决策场景

---

## 🤝 与其他 Skill 配合

### 与 Python Logging Skill 配合

- **Multi-Round Protocol**: 控制 AI 工作流
- **Python Logging**: 代码质量规范

两者可以结合使用：
```yaml
---TASK_STATUS---
status: completed
reason: 按照 Python Logging 规范重构了日志系统
confidence: 0.9
files_modified: [...]
applied_skills:
  - python-logging-best-practices
---END_STATUS---
```

---

## 📝 更新日志

- **v2.0.0** (2026-02-18)
  - 完全重写文档
  - 添加详细示例
  - 添加模板集合
  - 添加使用指南

- **v1.0.0** (2024-01-01)
  - 初始版本

---

**开始使用**: 从 `QUICKREF.md` 开始，5分钟掌握核心要点！

