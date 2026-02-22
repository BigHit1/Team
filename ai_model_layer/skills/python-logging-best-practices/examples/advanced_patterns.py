"""
高级日志模式示例

注意：运行此示例前，请确保：
1. 已安装项目依赖
2. 在项目根目录运行：python -m ai_model_layer.agents.skills.python-logging-best-practices.examples.advanced_patterns
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.utils.logger import get_logger
import time
from functools import wraps

logger = get_logger(__name__)


# 模式1: 性能监控装饰器
def log_performance(threshold_seconds=10):
    """记录函数执行时间的装饰器"""
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


@log_performance(threshold_seconds=0.05)
def slow_function():
    """模拟慢函数"""
    time.sleep(0.1)
    return "完成"


# 模式2: HTTP 请求处理
def handle_request(request_id, endpoint, params):
    """HTTP 请求处理示例"""
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
        # 模拟处理
        time.sleep(0.05)
        result = {"status": "success"}
        
        duration = time.time() - start_time
        req_logger.info("请求处理成功", extra={
            "duration_seconds": duration,
            "result_size": len(str(result))
        })
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        req_logger.error("请求处理失败", exc_info=True, extra={
            "duration_seconds": duration,
            "error_type": type(e).__name__
        })
        raise


# 模式3: 批量操作进度
def process_batch(items):
    """批量处理示例"""
    total = len(items)
    logger.info(f"开始批量处理", extra={
        "total_items": total
    })
    
    processed = 0
    errors = 0
    
    for i, item in enumerate(items):
        try:
            # 处理项目
            time.sleep(0.01)
            processed += 1
            
            # 每10%记录一次进度
            if (i + 1) % max(1, total // 10) == 0:
                logger.info(f"处理进度", extra={
                    "processed": i + 1,
                    "total": total,
                    "progress_percent": (i + 1) / total * 100
                })
                
        except Exception as e:
            errors += 1
            logger.error(f"处理项目失败", extra={
                "item_index": i,
                "error_type": type(e).__name__
            })
    
    logger.info("批量处理完成", extra={
        "total_items": total,
        "processed": processed,
        "errors": errors,
        "success_rate": processed / total if total > 0 else 0
    })


# 模式4: 数据库操作
def query_database(query, params):
    """数据库查询示例"""
    logger.debug("执行数据库查询", extra={
        "query": query[:100],  # 只记录前100个字符
        "params_count": len(params)
    })
    
    start_time = time.time()
    
    try:
        # 模拟查询
        time.sleep(0.02)
        result = [{"id": 1}, {"id": 2}]
        
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
        
    except Exception as e:
        logger.error("数据库查询失败", exc_info=True, extra={
            "query": query[:100],
            "error_type": type(e).__name__
        })
        raise


# 模式5: 文件处理
def process_file(file_path):
    """文件处理示例"""
    from pathlib import Path
    
    file_path = Path(file_path)
    
    logger.info("开始处理文件", extra={
        "file_path": str(file_path),
        "file_exists": file_path.exists()
    })
    
    if not file_path.exists():
        logger.error("文件不存在", extra={
            "file_path": str(file_path)
        })
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        # 模拟处理
        time.sleep(0.05)
        
        logger.info("文件处理完成", extra={
            "file_path": str(file_path),
            "success": True
        })
        
    except Exception as e:
        logger.error("文件处理失败", exc_info=True, extra={
            "file_path": str(file_path),
            "error_type": type(e).__name__
        })
        raise


if __name__ == "__main__":
    from ai_model_layer.utils.logger import setup_logging
    
    # 初始化日志系统
    setup_logging(log_dir="logs", console_level="DEBUG")
    
    print("=== 性能监控装饰器 ===")
    slow_function()
    
    print("\n=== HTTP 请求处理 ===")
    handle_request("req_123", "/api/data", {"key": "value"})
    
    print("\n=== 批量操作 ===")
    process_batch(list(range(25)))
    
    print("\n=== 数据库查询 ===")
    query_database("SELECT * FROM users WHERE id = ?", [1])
    
    print("\n=== 文件处理 ===")
    try:
        process_file("test.txt")
    except FileNotFoundError:
        pass

