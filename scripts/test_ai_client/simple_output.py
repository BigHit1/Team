"""
简单测试：验证 Claude Code CLI 输出捕获
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.config import get_config
from ai_model_layer.utils.logger import setup_logging, get_logger

# 初始化日志系统
setup_logging(
    log_dir="logs",
    console_level="INFO",
    file_level="DEBUG",
    enable_json=False
)

logger = get_logger(__name__)


def test_simple_output():
    """测试简单输出捕获"""
    logger.info("="*60)
    logger.info("测试：简单输出捕获")
    logger.info("="*60)
    
    # 从配置文件加载配置（会读取.env文件）
    config_manager = get_config()
    claude_config = config_manager.get_ai_client_config("claude_code")
    
    # 覆盖部分配置用于测试
    claude_config["timeout"] = 60
    claude_config["max_iterations"] = 1
    claude_config["auto_continue"] = False
    
    client = ClaudeCodeClient(claude_config)
    
    # 简单任务：只需要回答一个问题
    requirement = "请回答：1+1等于几？"
    
    try:
        result = client.execute_multi_round_task(
            requirement=requirement,
            project_path=str(project_root)
        )
        
        logger.info("="*60)
        logger.info("测试结果:")
        logger.info("="*60)
        logger.info(f"成功: {result['success']}")
        logger.info(f"耗时: {result['duration']:.1f}秒")
        
        output = result.get('final_output', '')
        logger.info(f"输出长度: {len(output)} 字符")
        logger.info("输出内容:")
        logger.info("-"*60)
        logger.info(output[:500] if len(output) > 500 else output)
        logger.info("-"*60)
        
        return len(output) > 0
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        success = test_simple_output()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"错误: {e}", exc_info=True)
        sys.exit(1)

