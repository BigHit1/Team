# Python 日志规范 Skill - 快速参考

## 🚀 快速开始

### 1. 初始化（应用入口）

```python
from ai_model_layer.utils.logger import setup_logging

setup_logging(log_dir="logs", console_level="INFO", file_level="DEBUG")
```

### 2. 使用（任何模块）

```python
from ai_model_layer.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("操作完成", extra={"key": "value"})
```

### 3. 带上下文（长任务）

```python
task_logger = get_logger(__name__, context={"task_id": task_id})
task_logger.info("任务开始")  # 自动包含 task_id
```

---

## 📋 日志级别速查

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | 函数参数、中间状态 |
| INFO | 重要操作 | 任务开始/完成 |
| WARNING | 可恢复问题 | 配置缺失、性能警告 |
| ERROR | 操作失败 | 异常、错误 |
| CRITICAL | 系统错误 | 无法启动 |

---

## ✅ 最佳实践

### 结构化日志
```python
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration": 45.2,
    "files": 100
})
```

### 性能监控
```python
start = time.time()
result = execute()
logger.debug("执行完成", extra={"duration": time.time() - start})
```

### 异常处理
```python
except Exception as e:
    logger.error("失败", exc_info=True, extra={
        "task_id": task_id,
        "error_type": type(e).__name__
    })
```

---

## ❌ 避免

```python
# ❌ 字符串拼接
logger.info(f"任务 {id} 完成，耗时 {t}秒")

# ❌ 缺少堆栈
logger.error(f"失败: {e}")

# ❌ 错误级别
logger.info("参数: ...")  # 应该用 DEBUG

# ❌ 敏感信息
logger.info(f"密码: {password}")
```

---

## 🔍 检查清单

- [ ] 使用正确的日志级别
- [ ] 使用 `extra` 参数添加结构化数据
- [ ] 异常使用 `exc_info=True`
- [ ] 长任务使用上下文日志器
- [ ] 记录关键操作耗时
- [ ] 敏感信息已脱敏

---

**详细文档**: 查看 [SKILL.md](SKILL.md)

