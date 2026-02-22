# Python 日志规范 Skill 使用指南

## 📦 Skill 结构

```
python-logging-best-practices/
├── README.md                    # Skill 概述
├── QUICKREF.md                  # 快速参考卡片（1页）
├── SKILL.md                     # 完整文档
├── skill.json                   # Skill 元数据
├── examples/                    # 代码示例
│   ├── basic_usage.py          # 基础使用示例
│   └── advanced_patterns.py    # 高级模式示例
└── templates/                   # 可复用模板
    ├── logger_template.py      # 代码模板
    ├── checklist.md            # 质量检查清单
    └── anti_patterns.md        # 反模式示例
```

## 🚀 如何使用此 Skill

### 1. 快速入门（5分钟）

阅读 `QUICKREF.md` 获取快速参考：
- 核心 API 使用
- 日志级别速查
- 最佳实践要点
- 常见错误避免

### 2. 深入学习（30分钟）

阅读 `SKILL.md` 了解完整规范：
- 6大核心原则详解
- 实施步骤指南
- 常见场景示例
- 反模式分析

### 3. 实践应用

#### 方式1: 查看示例代码

```bash
# 在项目根目录运行
cd d:/AI4UE_Plugin

# 运行基础示例
python -m ai_model_layer.agents.skills.python-logging-best-practices.examples.basic_usage

# 运行高级示例
python -m ai_model_layer.agents.skills.python-logging-best-practices.examples.advanced_patterns
```

#### 方式2: 使用代码模板

复制 `templates/logger_template.py` 中的模板到你的代码中：
- 模板1: 基础函数日志
- 模板2: 带性能监控的函数
- 模板3: 带上下文的任务处理
- 模板4: 批量操作
- 模板5: API 请求处理
- 模板6: 性能监控装饰器

#### 方式3: 代码审查

使用 `templates/checklist.md` 检查代码质量：
- 日志级别检查
- 日志内容检查
- 性能监控检查
- 异常处理检查
- 安全检查
- 代码质量检查

### 4. 团队培训

使用此 Skill 进行团队培训：
1. 分享 `QUICKREF.md` 作为速查表
2. 讲解 `SKILL.md` 中的核心原则
3. 演示 `examples/` 中的代码示例
4. 使用 `templates/anti_patterns.md` 讲解常见错误
5. 使用 `templates/checklist.md` 进行代码审查

## 📋 使用场景

### 场景1: 新项目建立日志系统

1. 阅读 `SKILL.md` 的"实施步骤"部分
2. 复制 `templates/logger_template.py` 中的初始化代码
3. 参考 `examples/basic_usage.py` 开始使用
4. 使用 `templates/checklist.md` 验证实施质量

### 场景2: 重构现有日志代码

1. 使用 `templates/checklist.md` 评估现有代码
2. 参考 `templates/anti_patterns.md` 识别问题
3. 使用 `templates/logger_template.py` 中的模板重构
4. 参考 `examples/advanced_patterns.py` 学习高级模式

### 场景3: 代码审查

1. 使用 `templates/checklist.md` 作为审查清单
2. 参考 `templates/anti_patterns.md` 识别反模式
3. 参考 `SKILL.md` 提供改进建议

### 场景4: 问题排查

1. 检查日志级别是否正确（参考 `QUICKREF.md`）
2. 检查是否包含足够的上下文信息
3. 检查异常是否记录完整堆栈
4. 参考 `SKILL.md` 的"日志分析"部分

## 🎯 学习路径

### 初级（1小时）
- [ ] 阅读 `README.md` 和 `QUICKREF.md`
- [ ] 运行 `examples/basic_usage.py`
- [ ] 理解 6 大核心原则
- [ ] 在项目中使用基础日志

### 中级（2小时）
- [ ] 阅读完整的 `SKILL.md`
- [ ] 运行 `examples/advanced_patterns.py`
- [ ] 学习使用上下文日志器
- [ ] 添加性能监控

### 高级（4小时）
- [ ] 深入理解所有模板
- [ ] 重构现有项目的日志
- [ ] 使用检查清单审查代码
- [ ] 建立团队日志规范

## 💡 最佳实践

### DO ✅

1. **使用结构化日志**
   ```python
   logger.info("任务完成", extra={"task_id": task_id, "duration": 45.2})
   ```

2. **使用上下文日志器**
   ```python
   task_logger = get_logger(__name__, context={"task_id": task_id})
   ```

3. **记录完整异常**
   ```python
   logger.error("失败", exc_info=True, extra={"task_id": task_id})
   ```

4. **监控性能**
   ```python
   logger.warning("耗时过长", extra={"duration_seconds": 15.5})
   ```

### DON'T ❌

1. **不要字符串拼接**
   ```python
   logger.info(f"任务 {id} 完成")  # ❌
   ```

2. **不要缺少堆栈**
   ```python
   logger.error(f"失败: {e}")  # ❌
   ```

3. **不要错误级别**
   ```python
   logger.info("参数: ...")  # ❌ 应该用 DEBUG
   ```

4. **不要记录敏感信息**
   ```python
   logger.info(f"密码: {password}")  # ❌
   ```

## 📚 参考资源

- **快速参考**: `QUICKREF.md`
- **完整文档**: `SKILL.md`
- **代码示例**: `examples/`
- **代码模板**: `templates/logger_template.py`
- **质量检查**: `templates/checklist.md`
- **反模式**: `templates/anti_patterns.md`

## 🤝 贡献

如果你有改进建议或发现问题，请：
1. 更新相关文档
2. 添加新的示例或模板
3. 完善检查清单

## 📝 更新日志

- **v1.0.0** (2026-02-18)
  - 初始版本
  - 包含完整的文档和示例
  - 提供代码模板和检查清单

---

**开始使用**: 从 `QUICKREF.md` 开始，5分钟掌握核心要点！

