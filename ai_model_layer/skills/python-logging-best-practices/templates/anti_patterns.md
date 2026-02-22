# 反模式示例 - 避免这些错误

## ❌ 反模式 1: 日志级别滥用

### 错误示例

```python
# 所有日志都用 INFO
logger.info(f"函数参数: {param1}, {param2}")  # 应该用 DEBUG
logger.info("配置文件不存在")  # 应该用 WARNING
logger.info("任务失败")  # 应该用 ERROR
```

### 正确示例

```python
logger.debug(f"函数参数: {param1}, {param2}")
logger.warning("配置文件不存在，使用默认配置")
logger.error("任务执行失败", exc_info=True)
```

---

## ❌ 反模式 2: 字符串拼接

### 错误示例

```python
logger.info(f"任务 {task_id} 完成，耗时 {duration}秒，处理 {count} 个文件")
```

### 正确示例

```python
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration_seconds": duration,
    "files_processed": count
})
```

---

## ❌ 反模式 3: 缺少异常信息

### 错误示例

```python
try:
    result = execute()
except Exception as e:
    logger.error(f"执行失败: {e}")  # 缺少堆栈
```

### 正确示例

```python
try:
    result = execute()
except Exception as e:
    logger.error("执行失败", exc_info=True, extra={
        "error_type": type(e).__name__,
        "error_message": str(e)
    })
```

---

## ❌ 反模式 4: 敏感信息泄露

### 错误示例

```python
logger.info(f"API Key: {api_key}")
logger.info(f"密码: {password}")
logger.info(f"用户邮箱: {email}")
```

### 正确示例

```python
logger.info(f"API Key: {api_key[:8]}***")
logger.debug("认证信息已设置")  # 不记录密码
logger.info(f"用户: {email[:3]}***@{email.split('@')[1]}")
```

---

## ❌ 反模式 5: 过度日志

### 错误示例

```python
# 在循环中记录过多日志
for item in items:
    logger.info(f"处理项目: {item}")  # 如果有10000个项目？
```

### 正确示例

```python
logger.info(f"开始处理 {len(items)} 个项目")
for i, item in enumerate(items):
    if i % 100 == 0:  # 每100个记录一次
        logger.debug(f"进度: {i}/{len(items)}")
logger.info(f"处理完成，共 {len(items)} 个项目")
```

---

## ❌ 反模式 6: 缺少上下文

### 错误示例

```python
logger.info("任务开始")
# ... 很多代码 ...
logger.info("阶段1完成")
# ... 很多代码 ...
logger.info("任务完成")
# 无法知道是哪个任务
```

### 正确示例

```python
task_logger = get_logger(__name__, context={"task_id": task_id})
task_logger.info("任务开始")
task_logger.info("阶段1完成")
task_logger.info("任务完成")
# 所有日志自动包含 task_id
```

---

## ❌ 反模式 7: 过多装饰

### 错误示例

```python
logger.info("="*60)
logger.info("开始执行任务")
logger.info("="*60)
logger.info(f"任务ID: {task_id}")
logger.info(f"项目: {project}")
logger.info("="*60)
```

### 正确示例

```python
logger.info("开始执行任务", extra={
    "task_id": task_id,
    "project": project
})
```

---

## ❌ 反模式 8: 信息分散

### 错误示例

```python
logger.info(f"任务完成: {task_id}")
logger.info(f"耗时: {duration}秒")
logger.info(f"处理文件: {file_count}个")
logger.info(f"成功率: {success_rate:.0%}")
```

### 正确示例

```python
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration_seconds": duration,
    "files_processed": file_count,
    "success_rate": success_rate
})
```

---

## ❌ 反模式 9: 缺少性能监控

### 错误示例

```python
def slow_operation():
    result = execute()  # 可能很慢
    return result
```

### 正确示例

```python
def slow_operation():
    start = time.time()
    result = execute()
    duration = time.time() - start
    
    if duration > 10:
        logger.warning("操作耗时过长", extra={
            "operation": "slow_operation",
            "duration_seconds": duration,
            "threshold_seconds": 10
        })
    
    return result
```

---

## ❌ 反模式 10: 使用 print

### 错误示例

```python
print("任务开始")
print(f"处理: {item}")
print("任务完成")
```

### 正确示例

```python
logger.info("任务开始")
logger.debug(f"处理项目", extra={"item": item})
logger.info("任务完成")
```

---

## 总结

避免这些反模式，让你的日志：

- ✅ 级别正确
- ✅ 结构化
- ✅ 包含完整信息
- ✅ 安全
- ✅ 简洁
- ✅ 有上下文
- ✅ 易于分析

