"""
测试日志系统
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_model_layer.utils.logger import setup_logging, get_logger


def test_basic_logging():
    """测试基础日志功能"""
    print("\n" + "="*60)
    print("测试基础日志功能")
    print("="*60)
    
    # 初始化日志系统
    setup_logging(
        log_dir="logs",
        console_level="DEBUG",
        file_level="DEBUG",
        enable_json=True
    )
    
    # 获取日志器
    logger = get_logger(__name__)
    
    # 测试各级别日志
    logger.debug("这是一条 DEBUG 日志")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    
    # 测试带参数的日志
    task_id = "task_123"
    iteration = 5
    logger.info(f"任务 {task_id} 第 {iteration} 轮开始执行")
    
    print("\n✓ 基础日志测试完成")


def test_context_logging():
    """测试上下文日志"""
    print("\n" + "="*60)
    print("测试上下文日志")
    print("="*60)
    
    # 带上下文的日志器
    logger = get_logger(__name__, context={
        "task_id": "task_456",
        "user_id": "user_789"
    })
    
    logger.info("这是一条带上下文的日志")
    logger.debug("上下文会自动添加到日志中")
    
    print("\n✓ 上下文日志测试完成")


def test_exception_logging():
    """测试异常日志"""
    print("\n" + "="*60)
    print("测试异常日志")
    print("="*60)
    
    logger = get_logger(__name__)
    
    try:
        # 故意触发异常
        result = 1 / 0
    except Exception as e:
        logger.error(f"捕获异常: {e}", exc_info=True)
        logger.exception("使用 exception 方法记录异常")
    
    print("\n✓ 异常日志测试完成")


def test_module_logging():
    """测试模块日志"""
    print("\n" + "="*60)
    print("测试模块日志")
    print("="*60)
    
    # 不同模块的日志器
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    logger1.info("来自 module1 的日志")
    logger2.info("来自 module2 的日志")
    
    print("\n✓ 模块日志测试完成")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("日志系统测试套件")
    print("="*60)
    
    try:
        # 测试基础日志
        test_basic_logging()
        
        # 测试上下文日志
        test_context_logging()
        
        # 测试异常日志
        test_exception_logging()
        
        # 测试模块日志
        test_module_logging()
        
        print("\n" + "="*60)
        print("所有测试通过！✓")
        print("="*60)
        print("\n请检查 logs 目录下的日志文件：")
        print("  - logs/ai4ue.log (主日志)")
        print("  - logs/ai4ue.error.log (错误日志)")
        print("  - logs/ai4ue.json.log (JSON 格式日志)")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

