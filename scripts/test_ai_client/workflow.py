"""
简单测试：验证完整 Workflow 执行
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
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


def test_workflow():
    """测试完整工作流"""
    logger.info("="*60)
    logger.info("测试：完整 Workflow 执行")
    logger.info("="*60)
    
    # 从配置文件加载配置
    config_manager = get_config()
    claude_config = config_manager.get_ai_client_config("claude_code")
    
    # 创建客户端
    client = ClaudeCodeClient(claude_config)
    
    # 创建编排器
    orchestrator = WorkflowOrchestrator(client=client)
    
    # 简单需求：创建一个简单的C++类
    requirement = """
创建一个简单的类，名为 ATestTestActor，具有以下功能：
1. 有一个 Health 属性（float类型）
2. 有一个 TakeDamage 函数
3. 添加必要的注释
4. 其他啥代码也不用写。
"""
    
    try:
        # 执行标准工作流
        result = orchestrator.execute_workflow(
            workflow_name="standard",
            requirement=requirement,
            project_path=str(project_root)
        )
        
        logger.info("="*60)
        logger.info("工作流执行结果:")
        logger.info("="*60)
        logger.info(f"成功: {result['success']}")
        logger.info(f"状态: {result['status']}")
        logger.info(f"总轮数: {result['total_iterations']}")
        logger.info(f"总耗时: {result['total_duration']:.1f}秒")
        
        logger.info(f"\n阶段详情 ({len(result['phases'])} 个):")
        for phase in result['phases']:
            logger.info(f"  - {phase.get('phase', 'unknown')}: {phase.get('final_status', 'unknown')} ({phase.get('iterations', 0)} 轮, {phase.get('duration', 0):.1f}秒)")
        
        if not result['success']:
            logger.error(f"失败阶段: {result.get('failed_phase')}")
            logger.error(f"错误: {result.get('error')}")
        
        return result['success']
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        success = test_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"错误: {e}", exc_info=True)
        sys.exit(1)

