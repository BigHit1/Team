"""
基础日志使用示例

注意：运行此示例前，请确保：
1. 已安装项目依赖
2. 在项目根目录运行：python -m ai_model_layer.agents.skills.python-logging-best-practices.examples.basic_usage
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.utils.logger import get_logger

logger = get_logger(__name__)


def example_basic():
    """基础日志示例"""
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误")


def example_structured():
    """结构化日志示例"""
    task_id = "task_123"
    duration = 45.2
    file_count = 100
    
    # ✅ 好：使用结构化数据
    logger.info("任务完成", extra={
        "task_id": task_id,
        "duration_seconds": duration,
        "files_processed": file_count,
        "success": True
    })


def example_context():
    """上下文日志示例"""
    task_id = "task_456"
    user_id = "user_789"
    
    # 创建带上下文的日志器
    task_logger = get_logger(__name__, context={
        "task_id": task_id,
        "user_id": user_id
    })
    
    # 所有日志自动包含上下文
    task_logger.info("任务开始")
    task_logger.info("阶段1完成")
    task_logger.info("任务完成")


def example_exception():
    """异常处理示例"""
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        # ✅ 好：记录完整堆栈
        logger.error("计算失败", exc_info=True, extra={
            "operation": "division",
            "error_type": type(e).__name__
        })


def example_performance():
    """性能监控示例"""
    import time
    
    start_time = time.time()
    
    # 执行操作
    time.sleep(0.1)
    
    duration = time.time() - start_time
    
    if duration > 0.05:
        logger.warning("操作耗时过长", extra={
            "operation": "process_data",
            "duration_seconds": duration,
            "threshold_seconds": 0.05
        })
    else:
        logger.debug("操作完成", extra={
            "operation": "process_data",
            "duration_seconds": duration
        })


if __name__ == "__main__":
    from ai_model_layer.utils.logger import setup_logging
    
    # 初始化日志系统
    setup_logging(log_dir="logs", console_level="DEBUG")
    
    print("=== 基础日志 ===")
    example_basic()
    
    print("\n=== 结构化日志 ===")
    example_structured()
    
    print("\n=== 上下文日志 ===")
    example_context()
    
    print("\n=== 异常处理 ===")
    example_exception()
    
    print("\n=== 性能监控 ===")
    example_performance()

