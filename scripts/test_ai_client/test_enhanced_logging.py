"""
测试增强的日志输出
验证输入输出和命令详细信息是否正确记录
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.config import AIConfig
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.utils.logger import get_logger

logger = get_logger(__name__)


def test_enhanced_logging():
    """测试增强的日志输出"""
    logger.info("="*60)
    logger.info("测试：增强的日志输出")
    logger.info("="*60)
    
    # 加载配置
    config_path = project_root / "config" / "ai_config.yaml"
    logger.info(f"加载配置: {config_path}")
    
    config = AIConfig.from_yaml(config_path)
    
    # 创建客户端
    logger.info("创建 Claude Code 客户端")
    client = ClaudeCodeClient(config.get_client_config("claude_code"))
    
    # 测试项目路径
    test_project = project_root / "test_projects" / "simple_test"
    test_project.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"测试项目路径: {test_project}")
    
    # 执行简单任务
    requirement = "请创建一个简单的 Python 文件 hello.py，内容是打印 'Hello, World!'"
    
    logger.info("="*60)
    logger.info("开始执行任务")
    logger.info("="*60)
    logger.info(f"需求: {requirement}")
    logger.info("="*60)
    
    try:
        result = client.execute_multi_round_task(
            requirement=requirement,
            project_path=str(test_project)
        )
        
        logger.info("="*60)
        logger.info("任务执行结果")
        logger.info("="*60)
        logger.info(f"成功: {result['success']}")
        logger.info(f"任务ID: {result['task_id']}")
        logger.info(f"迭代次数: {result['iterations']}")
        logger.info(f"总耗时: {result['duration']:.2f}秒")
        logger.info(f"最终状态: {result.get('final_status', 'unknown')}")
        
        if not result['success']:
            logger.error(f"错误: {result.get('error', 'unknown')}")
        
        logger.info("="*60)
        
        return result['success']
        
    except Exception as e:
        logger.error("="*60)
        logger.error("任务执行异常")
        logger.error("="*60)
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常信息: {str(e)}")
        logger.error("="*60)
        logger.error("异常堆栈:", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_enhanced_logging()
    sys.exit(0 if success else 1)

