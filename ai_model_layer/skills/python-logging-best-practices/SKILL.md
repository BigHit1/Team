# Python 日志规范 Skill

## 📋 Skill 信息

- **名称**: Python 日志规范
- **版本**: 1.0.0
- **作者**: AI4UE Team
- **用途**: 为 Python 项目建立企业级日志系统的完整规范和最佳实践

---

## 🎯 Skill 目标

当你需要为 Python 项目添加或重构日志系统时，使用此 Skill 可以：

1. ✅ 建立统一的日志规范
2. ✅ 实现结构化、可分析的日志
3. ✅ 正确使用日志级别
4. ✅ 添加上下文追踪
5. ✅ 记录性能指标
6. ✅ 完善异常处理

---

## 📚 核心原则

### 1. 结构化日志

**使用 `extra` 参数添加结构化数据**

```python
# ❌ 不好：字符串拼接
logger.info(f"任务完成: {task_id}, 耗时: {duration}秒, 文件数: {file_count}")

# ✅ 好：结构化数据
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration_seconds": duration,
    "files_modified": file_count,
    "success": True
})
```

**好处**:
- 便于日志分析和查询
- 支持 JSON 格式输出
- 易于集成监控系统

---

### 2. 上下文日志器

**为长时间运行的任务创建带上下文的日志器**

```python
from ai_model_layer.utils.logger import get_logger

# 创建带上下文的日志器
task_logger = get_logger(__name__, context={
    "task_id": task_id,
    "user_id": user_id,
    "workflow": workflow_name
})

# 所有日志自动包含上下文
task_logger.info("任务开始")  # 自动包含 task_id, user_id, workflow
task_logger.info("阶段1完成")  # 自动包含 task_id, user_id, workflow
task_logger.info("任务完成")  # 自动包含 task_id, user_id, workflow
```

**好处**:
- 自动追踪任务
- 便于日志过滤
- 减少重复代码

---

### 3. 正确的日志级别

#### DEBUG - 详细的调试信息

**用于**: 函数入口/出口、参数值、中间状态

```python
logger.debug("开始处理请求", extra={
    "function": "process_request",
    "params": {"param1": value1, "param2": value2}
})

logger.debug(f"中间结果: {intermediate_result}")

logger.debug("函数执行完成", extra={
    "function": "process_request",
    "execution_time": 0.5
})
```

#### INFO - 重要的业务操作

**用于**: 任务开始/完成、关键步骤、配置信息

```python
logger.info("任务开始执行", extra={
    "task_id": task_id,
    "task_type": "data_processing"
})

logger.info("数据处理完成", extra={
    "records_processed": 1000,
    "duration_seconds": 45.2
})

logger.info("服务启动", extra={
    "port": 8080,
    "environment": "production"
})
```

#### WARNING - 可恢复的问题

**用于**: 配置缺失、性能警告、弃用功能

```python
logger.warning("配置文件不存在，使用默认配置", extra={
    "config_file": config_path,
    "default_config": default_config
})

logger.warning("操作耗时过长", extra={
    "operation": "database_query",
    "duration_seconds": 15.5,
    "threshold_seconds": 10
})

logger.warning("此方法已弃用", extra={
    "deprecated_method": "old_method",
    "replacement": "new_method"
})
```

#### ERROR - 操作失败

**用于**: 异常、错误、操作失败

```python
logger.error("数据库连接失败", exc_info=True, extra={
    "database": "mysql",
    "host": "localhost",
    "port": 3306
})

logger.error("文件读取失败", extra={
    "file_path": file_path,
    "error_type": "FileNotFoundError"
})
```

#### CRITICAL - 系统级错误

**用于**: 系统无法启动、关键服务不可用

```python
logger.critical("数据库连接失败，系统无法启动", extra={
    "database": "mysql",
    "retry_count": 3
})

logger.critical("关键配置缺失", extra={
    "missing_config": ["API_KEY", "DATABASE_URL"]
})
```

---

### 4. 性能监控

**记录关键操作的耗时**

```python
import time

# 方法1: 手动计时
start_time = time.time()
result = execute_task()
duration = time.time() - start_time

if duration > 10:
    logger.warning("任务执行时间过长", extra={
        "task_id": task_id,
        "duration_seconds": duration,
        "threshold_seconds": 10
    })
else:
    logger.debug("任务执行完成", extra={
        "task_id": task_id,
        "duration_seconds": duration
    })

# 方法2: 使用装饰器（推荐）
from functools import wraps

def log_performance(threshold_seconds=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            logger_func = logger.warning if duration > threshold_seconds else logger.debug
            logger_func(f"函数执行完成: {func.__name__}", extra={
                "function": func.__name__,
                "duration_seconds": duration,
                "threshold_seconds": threshold_seconds
            })
            
            return result
        return wrapper
    return decorator

@log_performance(threshold_seconds=5)
def process_data(data):
    # 处理数据
    pass
```

---

### 5. 完善的异常处理

**记录完整的异常信息**

```python
try:
    result = execute_task()
except ValueError as e:
    # 预期的错误，记录 WARNING
    logger.warning("参数错误", extra={
        "task_id": task_id,
        "error_type": "ValueError",
        "error_message": str(e)
    })
except TimeoutError as e:
    # 超时错误，记录 ERROR + 完整堆栈
    logger.error("任务超时", exc_info=True, extra={
        "task_id": task_id,
        "timeout_seconds": timeout,
        "error_type": "TimeoutError"
    })
except Exception as e:
    # 未预期的错误，记录 ERROR + 完整堆栈
    logger.error("任务执行失败", exc_info=True, extra={
        "task_id": task_id,
        "iteration": iteration,
        "error_type": type(e).__name__,
        "error_message": str(e)
    })
    raise  # 重新抛出异常
```

**关键点**:
- ✅ 使用 `exc_info=True` 记录完整堆栈
- ✅ 记录错误类型 `type(e).__name__`
- ✅ 添加上下文信息（task_id, iteration 等）
- ✅ 区分预期/非预期错误

---

### 6. 减少冗余

**避免过多的装饰性日志**

```python
# ❌ 不好：过多装饰
logger.info("="*60)
logger.info("开始执行任务")
logger.info("="*60)
logger.info(f"任务ID: {task_id}")
logger.info(f"项目: {project}")
logger.info("="*60)

# ✅ 好：简洁明了
logger.info("开始执行任务", extra={
    "task_id": task_id,
    "project": project
})
```

**信息集中**

```python
# ❌ 不好：信息分散
logger.info(f"任务完成: {task_id}")
logger.info(f"耗时: {duration}秒")
logger.info(f"处理文件: {file_count}个")
logger.info(f"成功率: {success_rate:.0%}")

# ✅ 好：信息集中
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration_seconds": duration,
    "files_processed": file_count,
    "success_rate": success_rate
})
```

---

## 🛠️ 实施步骤

### 步骤 1: 初始化日志系统

在应用程序入口处（如 `main.py` 或 `__init__.py`）：

```python
from ai_model_layer.utils.logger import setup_logging

# 基础配置
setup_logging(
    log_dir="logs",
    console_level="INFO",
    file_level="DEBUG"
)

# 或使用环境配置
from ai_model_layer.utils.logging_config import get_config_by_env

config = get_config_by_env("production")  # development, production, testing
setup_logging(**config)
```

### 步骤 2: 在模块中使用

在每个模块中：

```python
from ai_model_layer.utils.logger import get_logger

# 获取日志器（使用模块名）
logger = get_logger(__name__)

# 使用日志
logger.info("模块初始化完成")
```

### 步骤 3: 为任务添加上下文

对于长时间运行的任务：

```python
from ai_model_layer.utils.logger import get_logger

def execute_task(task_id, user_id):
    # 创建带上下文的日志器
    task_logger = get_logger(__name__, context={
        "task_id": task_id,
        "user_id": user_id
    })
    
    task_logger.info("任务开始")
    # ... 执行任务 ...
    task_logger.info("任务完成")
```

### 步骤 4: 重构现有日志

按照以下优先级重构：

**P0 - 必须修复**:
1. 错误的日志级别（DEBUG/INFO 混用）
2. 缺少异常堆栈信息（`exc_info=True`）
3. 关键操作缺少日志

**P1 - 应该修复**:
1. 缺少上下文信息
2. 日志消息不够清晰
3. 缺少性能监控

**P2 - 可以优化**:
1. 减少冗余日志
2. 优化日志格式
3. 添加更多调试信息

---

## 📋 检查清单

使用此清单检查日志质量：

### 日志级别
- [ ] DEBUG: 用于详细调试信息
- [ ] INFO: 用于重要业务操作
- [ ] WARNING: 用于可恢复问题
- [ ] ERROR: 用于操作失败
- [ ] CRITICAL: 用于系统级错误

### 日志内容
- [ ] 包含关键上下文（task_id, user_id 等）
- [ ] 消息清晰简洁
- [ ] 包含操作结果
- [ ] 记录关键参数
- [ ] 使用结构化数据（extra）

### 性能监控
- [ ] 记录关键操作耗时
- [ ] 超时警告
- [ ] 性能指标（平均耗时、吞吐量等）

### 异常处理
- [ ] 记录完整堆栈（exc_info=True）
- [ ] 包含上下文信息
- [ ] 区分预期/非预期错误
- [ ] 记录错误类型

### 代码质量
- [ ] 避免重复日志
- [ ] 避免过多装饰性输出
- [ ] 使用上下文日志器
- [ ] 敏感信息脱敏

---

## 🎯 常见场景示例

### 场景 1: HTTP 请求处理

```python
from ai_model_layer.utils.logger import get_logger
import time

logger = get_logger(__name__)

def handle_request(request_id, endpoint, params):
    # 创建请求日志器
    req_logger = get_logger(__name__, context={
        "request_id": request_id,
        "endpoint": endpoint
    })
    
    req_logger.info("收到请求", extra={
        "method": "POST",
        "params_count": len(params)
    })
    
    start_time = time.time()
    
    try:
        result = process_request(params)
        duration = time.time() - start_time
        
        req_logger.info("请求处理成功", extra={
            "duration_seconds": duration,
            "result_size": len(result)
        })
        
        return result
        
    except ValueError as e:
        req_logger.warning("参数验证失败", extra={
            "error": str(e)
        })
        raise
        
    except Exception as e:
        duration = time.time() - start_time
        req_logger.error("请求处理失败", exc_info=True, extra={
            "duration_seconds": duration,
            "error_type": type(e).__name__
        })
        raise
```

### 场景 2: 数据库操作

```python
from ai_model_layer.utils.logger import get_logger
import time

logger = get_logger(__name__)

def query_database(query, params):
    logger.debug("执行数据库查询", extra={
        "query": query[:100],  # 只记录前100个字符
        "params_count": len(params)
    })
    
    start_time = time.time()
    
    try:
        result = db.execute(query, params)
        duration = time.time() - start_time
        
        if duration > 1.0:
            logger.warning("查询耗时过长", extra={
                "query": query[:100],
                "duration_seconds": duration,
                "threshold_seconds": 1.0,
                "rows_returned": len(result)
            })
        else:
            logger.debug("查询完成", extra={
                "duration_seconds": duration,
                "rows_returned": len(result)
            })
        
        return result
        
    except DatabaseError as e:
        logger.error("数据库查询失败", exc_info=True, extra={
            "query": query[:100],
            "error_type": type(e).__name__,
            "error_code": e.code if hasattr(e, 'code') else None
        })
        raise
```

### 场景 3: 文件处理

```python
from ai_model_layer.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)

def process_file(file_path):
    file_path = Path(file_path)
    
    logger.info("开始处理文件", extra={
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size if file_path.exists() else 0
    })
    
    if not file_path.exists():
        logger.error("文件不存在", extra={
            "file_path": str(file_path)
        })
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = f.read()
        
        result = process_data(data)
        
        logger.info("文件处理完成", extra={
            "file_path": str(file_path),
            "lines_processed": len(data.splitlines()),
            "result_size": len(result)
        })
        
        return result
        
    except Exception as e:
        logger.error("文件处理失败", exc_info=True, extra={
            "file_path": str(file_path),
            "error_type": type(e).__name__
        })
        raise
```

### 场景 4: 异步任务

```python
from ai_model_layer.utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

async def async_task(task_id, data):
    # 创建任务日志器
    task_logger = get_logger(__name__, context={
        "task_id": task_id,
        "task_type": "async_processing"
    })
    
    task_logger.info("异步任务开始", extra={
        "data_size": len(data)
    })
    
    try:
        result = await process_async(data)
        
        task_logger.info("异步任务完成", extra={
            "result_size": len(result),
            "success": True
        })
        
        return result
        
    except asyncio.TimeoutError:
        task_logger.error("异步任务超时", extra={
            "timeout_seconds": 30
        })
        raise
        
    except Exception as e:
        task_logger.error("异步任务失败", exc_info=True, extra={
            "error_type": type(e).__name__
        })
        raise
```

---

## 🚫 反模式（避免）

### 反模式 1: 日志级别滥用

```python
# ❌ 不好：所有日志都用 INFO
logger.info(f"函数参数: {param1}, {param2}")  # 应该用 DEBUG
logger.info("配置文件不存在")  # 应该用 WARNING
logger.info("任务失败")  # 应该用 ERROR

# ✅ 好：正确使用级别
logger.debug(f"函数参数: {param1}, {param2}")
logger.warning("配置文件不存在，使用默认配置")
logger.error("任务执行失败", exc_info=True)
```

### 反模式 2: 字符串拼接

```python
# ❌ 不好：字符串拼接
logger.info(f"任务 {task_id} 完成，耗时 {duration}秒，处理 {count} 个文件")

# ✅ 好：结构化数据
logger.info("任务完成", extra={
    "task_id": task_id,
    "duration_seconds": duration,
    "files_processed": count
})
```

### 反模式 3: 缺少异常信息

```python
# ❌ 不好：只记录错误消息
try:
    result = execute()
except Exception as e:
    logger.error(f"执行失败: {e}")  # 缺少堆栈

# ✅ 好：记录完整堆栈
try:
    result = execute()
except Exception as e:
    logger.error("执行失败", exc_info=True, extra={
        "error_type": type(e).__name__,
        "error_message": str(e)
    })
```

### 反模式 4: 敏感信息泄露

```python
# ❌ 不好：记录敏感信息
logger.info(f"API Key: {api_key}")
logger.info(f"密码: {password}")
logger.info(f"用户邮箱: {email}")

# ✅ 好：脱敏处理
logger.info(f"API Key: {api_key[:8]}***")
logger.debug("认证信息已设置")  # 不记录密码
logger.info(f"用户: {email[:3]}***@{email.split('@')[1]}")
```

### 反模式 5: 过度日志

```python
# ❌ 不好：在循环中记录过多日志
for item in items:
    logger.info(f"处理项目: {item}")  # 如果有10000个项目？

# ✅ 好：批量记录或采样
logger.info(f"开始处理 {len(items)} 个项目")
for i, item in enumerate(items):
    if i % 100 == 0:  # 每100个记录一次
        logger.debug(f"进度: {i}/{len(items)}")
logger.info(f"处理完成，共 {len(items)} 个项目")
```

---

## 📊 日志分析

### 使用 grep 查询日志

```bash
# 查询特定任务的日志
grep "task_123" logs/ai4ue.log

# 查询错误日志
grep "ERROR" logs/ai4ue.log

# 查询耗时过长的操作
grep "duration_seconds" logs/ai4ue.log | grep -E "duration_seconds\":\s*[0-9]{2,}"
```

### 使用 jq 分析 JSON 日志

```bash
# 查询所有错误
jq 'select(.level == "ERROR")' logs/ai4ue.json.log

# 统计错误类型
jq -r 'select(.level == "ERROR") | .error_type' logs/ai4ue.json.log | sort | uniq -c

# 查询耗时最长的操作
jq 'select(.duration_seconds != null) | {message, duration_seconds}' logs/ai4ue.json.log | jq -s 'sort_by(.duration_seconds) | reverse | .[0:10]'

# 查询特定任务的所有日志
jq 'select(.context.task_id == "task_123")' logs/ai4ue.json.log
```

---

## 🎓 总结

### 核心要点

1. **结构化日志** - 使用 `extra` 参数
2. **上下文追踪** - 使用上下文日志器
3. **正确级别** - DEBUG/INFO/WARNING/ERROR/CRITICAL
4. **性能监控** - 记录关键操作耗时
5. **完整异常** - `exc_info=True` + 上下文
6. **减少冗余** - 信息集中、简洁明了

### 记住

- ✅ 日志是为了**调试**和**监控**，不是为了装饰
- ✅ 结构化数据比字符串拼接更有价值
- ✅ 上下文信息是问题定位的关键
- ✅ 性能指标帮助发现瓶颈
- ✅ 完整的异常信息节省调试时间

---

## 📚 参考资源

- [Python logging 官方文档](https://docs.python.org/3/library/logging.html)
- [Python logging 最佳实践](https://docs.python-guide.org/writing/logging/)
- [结构化日志指南](https://www.structlog.org/)
- [12-Factor App: Logs](https://12factor.net/logs)
- [项目日志系统指南](../../docs/LOGGING_GUIDE.md)

---

**使用此 Skill，让你的 Python 项目拥有企业级的日志质量！** 🎉

