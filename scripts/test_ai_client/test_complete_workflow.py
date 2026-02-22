"""
测试完整工作流
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.utils.logger import setup_logging, get_logger

# 初始化日志系统
setup_logging(
    log_dir="logs",
    console_level="INFO",
    file_level="DEBUG",
    enable_json=False
)

# 获取日志器
logger = get_logger(__name__)


def test_complete_workflow():
    """测试完整工作流"""
    logger.info("="*60)
    logger.info("测试完整工作流（包含所有 7 个 Agent）")
    logger.info("="*60)
    
    orchestrator = WorkflowOrchestrator()
    
    # 加载完整工作流
    workflow = orchestrator.load_workflow("complete")
    
    if not workflow:
        logger.error("完整工作流加载失败")
        return
    
    logger.info(f"工作流: {workflow['name']}")
    logger.info(f"描述: {workflow['description']}")
    logger.info(f"阶段数量: {len(workflow['phases'])}")
    
    logger.info("工作流阶段：")
    for i, phase in enumerate(workflow['phases'], 1):
        logger.info(f"  {i}. {phase.name}")
        logger.debug(f"     Agent: {phase.agent}")
        logger.debug(f"     描述: {phase.description}")
        logger.debug(f"     最大迭代: {phase.max_iterations}")
        if phase.depends_on:
            logger.debug(f"     依赖: {phase.depends_on}")
    
    # 干运行测试
    logger.info("="*60)
    logger.info("干运行测试完整工作流")
    logger.info("="*60)
    
    requirement = "实现一个完整的武器系统，包括开火、换弹、伤害计算、网络同步"
    
    result = orchestrator.execute_workflow(
        workflow_name="complete",
        requirement=requirement,
        dry_run=True
    )
    
    logger.info("干运行结果:")
    logger.info(f"  状态: {result['status']}")
    logger.info(f"  执行的阶段数: {len(result['phases'])}")
    logger.info(f"  总耗时: {result['total_duration']:.2f}秒")
    
    logger.info("各阶段状态：")
    for phase_result in result['phases']:
        if phase_result['status'] == 'completed':
            logger.info(f"  {phase_result['phase']} ({phase_result['agent']})")
        else:
            logger.error(f"  {phase_result['phase']} ({phase_result['agent']})")
    
    if result['success']:
        logger.info("完整工作流测试通过！")
    else:
        logger.error(f"完整工作流测试失败: {result.get('error')}")


if __name__ == "__main__":
    test_complete_workflow()

