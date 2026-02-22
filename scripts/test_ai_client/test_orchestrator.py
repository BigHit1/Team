"""
测试 Agent 编排系统
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_model_layer.agents.agent_library import AgentLibrary
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


def test_agent_library():
    """测试 Agent 库"""
    logger.info("="*60)
    logger.info("测试 Agent 库")
    logger.info("="*60)
    
    library = AgentLibrary()
    
    # 列出所有 Agent
    agents = library.list_agents()
    logger.info(f"可用的 Agent 数量: {len(agents)}")
    for agent_name, description in agents.items():
        logger.info(f"  - {agent_name}: {description}")
    
    # 加载一个 Agent
    logger.info("加载 planner Agent:")
    planner = library.get_agent("planner")
    if planner:
        logger.info(f"  名称: {planner['name']}")
        logger.info(f"  描述: {planner['description']}")
        logger.info(f"  提示词长度: {len(planner['prompt'])} 字符")
    
    logger.info("Agent 库测试通过")


def test_workflow_orchestrator():
    """测试工作流编排器"""
    logger.info("="*60)
    logger.info("测试工作流编排器")
    logger.info("="*60)
    
    orchestrator = WorkflowOrchestrator()
    
    # 列出所有工作流
    workflows = orchestrator.list_workflows()
    logger.info(f"可用的工作流数量: {len(workflows)}")
    for workflow in workflows:
        logger.info(f"  - {workflow}")
    
    # 加载一个工作流
    logger.info("加载 standard 工作流:")
    workflow = orchestrator.load_workflow("standard")
    if workflow:
        logger.info(f"  名称: {workflow['name']}")
        logger.info(f"  描述: {workflow['description']}")
        logger.info(f"  阶段数量: {len(workflow['phases'])}")
        
        for i, phase in enumerate(workflow['phases'], 1):
            logger.info(f"  阶段 {i}: {phase.name}")
            logger.debug(f"    Agent: {phase.agent}")
            logger.debug(f"    描述: {phase.description}")
            logger.debug(f"    最大迭代: {phase.max_iterations}")
    
    logger.info("工作流编排器测试通过")


def test_dry_run():
    """测试干运行（不实际执行 Claude Code）"""
    logger.info("="*60)
    logger.info("测试干运行")
    logger.info("="*60)
    
    orchestrator = WorkflowOrchestrator()
    
    requirement = "实现一个简单的武器系统，包括开火和换弹功能"
    
    logger.info(f"需求: {requirement}")
    logger.info("开始干运行...")
    
    try:
        # 使用 dry_run 模式
        result = orchestrator.execute_workflow(
            workflow_name="quick",
            requirement=requirement,
            dry_run=True  # 干运行模式
        )
        
        logger.info("干运行结果:")
        logger.info(f"  工作流: {result['workflow']}")
        logger.info(f"  状态: {result['status']}")
        logger.info(f"  执行的阶段数: {len(result['phases'])}")
        
        for phase_result in result['phases']:
            logger.info(f"  阶段: {phase_result['phase']}")
            logger.debug(f"    Agent: {phase_result['agent']}")
            logger.debug(f"    状态: {phase_result['status']}")
            if phase_result.get('output_file'):
                logger.debug(f"    输出文件: {phase_result['output_file']}")
        
        logger.info("干运行测试通过")
        
    except Exception as e:
        logger.error(f"干运行测试失败: {e}", exc_info=True)


def main():
    """主测试函数"""
    logger.info("="*60)
    logger.info("Agent 编排系统测试套件")
    logger.info("="*60)
    
    try:
        # 测试 Agent 库
        test_agent_library()
        
        # 测试工作流编排器
        test_workflow_orchestrator()
        
        # 测试干运行
        test_dry_run()
        
        logger.info("="*60)
        logger.info("所有测试通过！")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

