"""
测试 Orchestrator 输出显示
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.utils.logger import setup_logging, get_logger

setup_logging(log_dir="logs", console_level="INFO", file_level="DEBUG", enable_json=False)
logger = get_logger(__name__)

def test_orchestrator():
    """测试 Orchestrator 输出"""
    
    config = {
        "api_key": "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o",
        "api_base_url": "https://synai996.space/",
        "model": "opus",
        "timeout": 60,
        "max_iterations": 1,
        "auto_continue": False
    }
    
    client = ClaudeCodeClient(config)
    orchestrator = WorkflowOrchestrator(client=client)
    
    # 创建简单的单阶段工作流
    phases = orchestrator.create_custom_workflow([
        {
            "name": "test",
            "agent": "planner",
            "description": "测试阶段",
            "requirement": "请回答：2+2等于几？",
            "max_iterations": 1,
            "timeout": 60
        }
    ])
    
    result = orchestrator.execute_phases(
        phases=phases,
        requirement="测试需求",
        project_path=str(project_root)
    )
    
    logger.info("="*60)
    logger.info(f"工作流结果: {'成功' if result['success'] else '失败'}")
    logger.info(f"总耗时: {result['total_duration']:.1f}秒")
    logger.info("="*60)
    
    return result['success']

if __name__ == "__main__":
    try:
        success = test_orchestrator()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        sys.exit(1)

