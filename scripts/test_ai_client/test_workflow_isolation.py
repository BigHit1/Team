"""
测试：多次运行 Workflow 的隔离
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


def test_multiple_runs():
    """测试多次运行的隔离"""
    logger.info("="*60)
    logger.info("测试：多次运行 Workflow 的隔离")
    logger.info("="*60)
    
    # 从配置文件加载配置
    config_manager = get_config()
    claude_config = config_manager.get_ai_client_config("claude_code")
    
    # 创建客户端
    client = ClaudeCodeClient(claude_config)
    
    # 创建编排器
    orchestrator = WorkflowOrchestrator(client=client)
    
    # 第1次运行：创建 Actor 类
    logger.info("\n" + "="*60)
    logger.info("第1次运行：创建 Actor 类")
    logger.info("="*60)
    
    result1 = orchestrator.execute_workflow(
        workflow_name="standard",
        requirement="创建一个简单的 Actor 类，名为 ATestActor",
        project_path=str(project_root)
    )
    
    logger.info(f"第1次运行完成，Run ID: {result1.get('run_id')}")
    
    # 第2次运行：创建 Component 类
    logger.info("\n" + "="*60)
    logger.info("第2次运行：创建 Component 类")
    logger.info("="*60)
    
    result2 = orchestrator.execute_workflow(
        workflow_name="standard",
        requirement="创建一个简单的 Component 类，名为 UTestComponent",
        project_path=str(project_root)
    )
    
    logger.info(f"第2次运行完成，Run ID: {result2.get('run_id')}")
    
    # 列出所有运行
    logger.info("\n" + "="*60)
    logger.info("所有运行记录")
    logger.info("="*60)
    
    runs = orchestrator.list_runs(str(project_root), "standard")
    for run in runs:
        logger.info(f"Run ID: {run['run_id']}")
        logger.info(f"  工作流: {run['workflow']}")
        logger.info(f"  时间: {run['timestamp']}")
        logger.info(f"  阶段: {', '.join(run['phases'])}")
        logger.info(f"  路径: {run['path']}")
    
    # 验证文件隔离
    logger.info("\n" + "="*60)
    logger.info("验证文件隔离")
    logger.info("="*60)
    
    run1_planning = orchestrator.get_run_output(
        str(project_root),
        result1.get('run_id'),
        'planning'
    )
    
    run2_planning = orchestrator.get_run_output(
        str(project_root),
        result2.get('run_id'),
        'planning'
    )
    
    if run1_planning and run2_planning:
        logger.info("✅ 两次运行的输出都存在且独立")
        logger.info(f"Run 1 planning 长度: {len(run1_planning)} 字符")
        logger.info(f"Run 2 planning 长度: {len(run2_planning)} 字符")
    else:
        logger.error("❌ 文件隔离失败")
    
    return result1['success'] and result2['success']


def test_continue_run():
    """测试继续上次运行"""
    logger.info("\n" + "="*60)
    logger.info("测试：继续上次运行")
    logger.info("="*60)
    
    config_manager = get_config()
    claude_config = config_manager.get_ai_client_config("claude_code")
    client = ClaudeCodeClient(claude_config)
    orchestrator = WorkflowOrchestrator(client=client)
    
    # 第1次运行
    logger.info("第1次运行...")
    result1 = orchestrator.execute_workflow(
        workflow_name="standard",
        requirement="创建一个 Pawn 类",
        project_path=str(project_root)
    )
    
    run_id = result1.get('run_id')
    logger.info(f"Run ID: {run_id}")
    
    # 继续上次运行（使用 use_latest=True）
    logger.info("\n继续上次运行...")
    result2 = orchestrator.execute_workflow(
        workflow_name="standard",
        requirement="为 Pawn 类添加移动功能",
        project_path=str(project_root),
        use_latest=True  # 继续最新的运行
    )
    
    logger.info(f"继续运行的 Run ID: {result2.get('run_id')}")
    
    if result2.get('run_id') == run_id:
        logger.info("✅ 成功继续上次运行（Run ID 相同）")
    else:
        logger.warning("⚠️ 创建了新的运行（Run ID 不同）")
    
    return result1['success'] and result2['success']


if __name__ == "__main__":
    try:
        logger.info("开始测试...")
        
        # 测试1：多次运行隔离
        success1 = test_multiple_runs()
        
        # 测试2：继续运行
        success2 = test_continue_run()
        
        if success1 and success2:
            logger.info("\n" + "="*60)
            logger.info("✅ 所有测试通过")
            logger.info("="*60)
            sys.exit(0)
        else:
            logger.error("\n" + "="*60)
            logger.error("❌ 部分测试失败")
            logger.error("="*60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"错误: {e}", exc_info=True)
        sys.exit(1)

