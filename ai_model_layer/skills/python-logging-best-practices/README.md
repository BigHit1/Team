# Python 日志规范 Skill

企业级 Python 日志系统的完整规范和最佳实践。

## 📁 文件说明

- **QUICKREF.md** - 快速参考卡片（1页）
- **SKILL.md** - 完整的 Skill 文档（包含原则、示例、检查清单）
- **examples/** - 实际代码示例
- **templates/** - 可复用的代码模板

## 🚀 快速开始

### 1. 初始化日志系统

```python
from ai_model_layer.utils.logger import setup_logging

setup_logging(log_dir="logs", console_level="INFO", file_level="DEBUG")
```

### 2. 在模块中使用

```python
from ai_model_layer.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("操作完成", extra={"key": "value"})
```

### 3. 带上下文的日志

```python
task_logger = get_logger(__name__, context={"task_id": task_id})
task_logger.info("任务开始")  # 自动包含 task_id
```

## 📋 核心原则

1. **结构化日志** - 使用 `extra` 参数添加结构化数据
2. **上下文追踪** - 为长任务创建带上下文的日志器
3. **正确级别** - DEBUG/INFO/WARNING/ERROR/CRITICAL
4. **性能监控** - 记录关键操作耗时
5. **完整异常** - 使用 `exc_info=True` 记录堆栈
6. **减少冗余** - 信息集中、简洁明了

## 📚 文档

- [快速参考](QUICKREF.md) - 1页速查表
- [完整文档](SKILL.md) - 详细的规范和示例
- [代码示例](examples/) - 实际场景的代码示例
- [模板](templates/) - 可复用的代码模板

## ✅ 检查清单

- [ ] 使用正确的日志级别
- [ ] 使用 `extra` 参数添加结构化数据
- [ ] 异常使用 `exc_info=True`
- [ ] 长任务使用上下文日志器
- [ ] 记录关键操作耗时
- [ ] 敏感信息已脱敏

## 🎯 适用场景

- ✅ 新项目建立日志系统
- ✅ 重构现有日志代码
- ✅ 代码审查日志质量
- ✅ 团队日志规范培训

## 📊 效果

使用此 Skill 后，你的日志将：

- ✅ 易于查询和分析
- ✅ 包含完整的上下文信息
- ✅ 便于问题定位和调试
- ✅ 支持性能监控和优化
- ✅ 符合企业级标准

---

**版本**: 1.0.0  
**作者**: AI4UE Team  
**更新**: 2026-02-18

