"""
日志模板 - 可复用的代码片段
"""

from ai_model_layer.utils.logger import get_logger
import time
from functools import wraps

logger = get_logger(__name__)


# ============================================================
# 模板1: 基础函数日志
# ============================================================

def template_basic_function(param1, param2):
    """基础函数日志模板"""
    logger.debug("函数开始", extra={
        "function": "template_basic_function",
        "param1": param1,
        "param2": param2
    })
    
    try:
        # 执行操作
        result = param1 + param2
        
        logger.info("函数完成", extra={
            "function": "template_basic_function",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error("函数失败", exc_info=True, extra={
            "function": "template_basic_function",
            "error_type": type(e).__name__
        })
        raise


# ============================================================
# 模板2: 带性能监控的函数
# ============================================================

def template_with_performance(data):
    """带性能监控的函数模板"""
    start_time = time.time()
    
    logger.info("操作开始", extra={
        "operation": "template_with_performance",
        "data_size": len(data)
    })
    
    try:
        # 执行操作
        result = process_data(data)
        
        duration = time.time() - start_time
        
        if duration > 10:
            logger.warning("操作耗时过长", extra={
                "operation": "template_with_performance",
                "duration_seconds": duration,
                "threshold_seconds": 10
            })
        else:
            logger.info("操作完成", extra={
                "operation": "template_with_performance",
                "duration_seconds": duration
            })
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error("操作失败", exc_info=True, extra={
            "operation": "template_with_performance",
            "duration_seconds": duration,
            "error_type": type(e).__name__
        })
        raise


# ============================================================
# 模板3: 带上下文的任务处理
# ============================================================

def template_task_with_context(task_id, user_id, data):
    """带上下文的任务处理模板"""
    # 创建任务日志器
    task_logger = get_logger(__name__, context={
        "task_id": task_id,
        "user_id": user_id
    })
    
    task_logger.info("任务开始", extra={
        "data_size": len(data)
    })
    
    start_time = time.time()
    
    try:
        # 阶段1
        task_logger.info("阶段1: 数据验证")
        validate_data(data)
        
        # 阶段2
        task_logger.info("阶段2: 数据处理")
        result = process_data(data)
        
        # 阶段3
        task_logger.info("阶段3: 结果保存")
        save_result(result)
        
        duration = time.time() - start_time
        task_logger.info("任务完成", extra={
            "duration_seconds": duration,
            "result_size": len(result)
        })
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        task_logger.error("任务失败", exc_info=True, extra={
            "duration_seconds": duration,
            "error_type": type(e).__name__
        })
        raise


# ============================================================
# 模板4: 批量操作
# ============================================================

def template_batch_processing(items):
    """批量操作模板"""
    total = len(items)
    
    logger.info("批量操作开始", extra={
        "total_items": total
    })
    
    processed = 0
    errors = 0
    error_items = []
    
    for i, item in enumerate(items):
        try:
            # 处理项目
            process_item(item)
            processed += 1
            
            # 每10%记录进度
            if (i + 1) % max(1, total // 10) == 0:
                logger.info("处理进度", extra={
                    "processed": i + 1,
                    "total": total,
                    "progress_percent": (i + 1) / total * 100
                })
                
        except Exception as e:
            errors += 1
            error_items.append(i)
            logger.error("处理项目失败", extra={
                "item_index": i,
                "error_type": type(e).__name__
            })
    
    logger.info("批量操作完成", extra={
        "total_items": total,
        "processed": processed,
        "errors": errors,
        "success_rate": processed / total if total > 0 else 0,
        "error_items": error_items[:10]  # 只记录前10个错误
    })
    
    return {
        "processed": processed,
        "errors": errors,
        "error_items": error_items
    }


# ============================================================
# 模板5: API 请求处理
# ============================================================

def template_api_request(request_id, endpoint, method, params):
    """API 请求处理模板"""
    # 创建请求日志器
    req_logger = get_logger(__name__, context={
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method
    })
    
    req_logger.info("收到请求", extra={
        "params_count": len(params)
    })
    
    start_time = time.time()
    
    try:
        # 验证参数
        req_logger.debug("验证参数")
        validate_params(params)
        
        # 处理请求
        req_logger.debug("处理请求")
        result = handle_api_request(endpoint, params)
        
        duration = time.time() - start_time
        req_logger.info("请求成功", extra={
            "duration_seconds": duration,
            "result_size": len(str(result))
        })
        
        return result
        
    except ValueError as e:
        # 参数错误 - WARNING
        req_logger.warning("参数验证失败", extra={
            "error": str(e)
        })
        raise
        
    except Exception as e:
        # 其他错误 - ERROR
        duration = time.time() - start_time
        req_logger.error("请求失败", exc_info=True, extra={
            "duration_seconds": duration,
            "error_type": type(e).__name__
        })
        raise


# ============================================================
# 模板6: 性能监控装饰器
# ============================================================

def log_performance(threshold_seconds=10):
    """性能监控装饰器模板"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            
            logger.debug(f"函数开始: {func.__name__}", extra={
                "function": func.__name__
            })
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                logger_func = logger.warning if duration > threshold_seconds else logger.debug
                logger_func(f"函数完成: {func.__name__}", extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "threshold_seconds": threshold_seconds
                })
                
                return result
                
            except Exception as e:
                duration = time.time() - start
                logger.error(f"函数失败: {func.__name__}", exc_info=True, extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "error_type": type(e).__name__
                })
                raise
                
        return wrapper
    return decorator


# ============================================================
# 辅助函数（示例）
# ============================================================

def process_data(data):
    """处理数据（示例）"""
    return data

def validate_data(data):
    """验证数据（示例）"""
    pass

def save_result(result):
    """保存结果（示例）"""
    pass

def process_item(item):
    """处理项目（示例）"""
    pass

def validate_params(params):
    """验证参数（示例）"""
    pass

def handle_api_request(endpoint, params):
    """处理 API 请求（示例）"""
    return {"status": "success"}

