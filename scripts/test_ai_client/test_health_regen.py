
import sys
import os
import argparse
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#python scripts/test_health_regen.py --project F:\UE5 --full
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.utils.logger import setup_logging, get_logger
from ai_model_layer.config import get_config


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='测试生命恢复功能工作流')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='干运行模式（验证配置）')
    group.add_argument('--quick', action='store_true', help='快速工作流（Plan + Code）')
    group.add_argument('--full', action='store_true', help='完整工作流（Plan + Arch + Code + Review）')
    
    parser.add_argument('--project', type=str, help='Lyra 项目路径（默认从环境变量读取）')
    parser.add_argument('--api-key', type=str, help='Anthropic API Key（默认从环境变量读取）')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 初始化日志
    setup_logging(
        log_dir="logs",
        console_level="INFO",
        file_level="DEBUG",
        enable_json=True
    )
    logger = get_logger(__name__)
    
    logger.info("="*80)
    logger.info("生命恢复功能工作流测试")
    logger.info("="*80)
    
    # 加载需求
    requirement_file = Path(__file__).parent.parent / "requirements/examples/add_health_regen_ability.md"
    if not requirement_file.exists():
        logger.error(f"需求文件不存在: {requirement_file}")
        sys.exit(1)
    
    requirement = requirement_file.read_text(encoding='utf-8')
    logger.info(f"需求文档: {requirement_file.name}")
    logger.info("")
    
    # 干运行模式
    if args.dry_run:
        logger.info("模式: 干运行（验证配置）")
        logger.info("")
        
        orchestrator = WorkflowOrchestrator()
        
        result = orchestrator.execute_workflow(
            workflow_name="standard",
            requirement=requirement,
            dry_run=True
        )
        
        logger.info("")
        logger.info("="*80)
        if result['success']:
            logger.info("✅ 配置验证通过")
        else:
            logger.error(f"❌ 配置验证失败: {result.get('error')}")
            sys.exit(1)
        logger.info("="*80)
        return
    
    # 实际执行模式
    # 获取项目路径
    project_path = args.project or os.getenv("LYRA_PROJECT_PATH")
    if not project_path:
        logger.error("错误: 未指定项目路径")
        logger.info("请使用 --project 参数或设置环境变量 LYRA_PROJECT_PATH")
        logger.info("示例: python scripts/test_health_regen.py --quick --project D:\\UE5Projects\\LyraStarterGame")
        sys.exit(1)
    
    if not Path(project_path).exists():
        logger.error(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)
    
    logger.info(f"项目路径: {project_path}")
    
    # 获取 API Key
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        logger.error("错误: 未设置 API Key")
        logger.info("请使用 --api-key 参数或设置环境变量 ANTHROPIC_API_KEY")
        logger.info("示例: python scripts/test_health_regen.py --quick --api-key sk-xxx")
        sys.exit(1)
    
    logger.info("API Key: " + api_key[:20] + "..." if len(api_key) > 20 else api_key)
    
    # 选择工作流
    if args.quick:
        workflow_name = "quick"
        logger.info("模式: 快速工作流（Plan + Code）")
    else:
        workflow_name = "standard"
        logger.info("模式: 完整工作流（Plan + Arch + Code + Review）")
    
    logger.info("")
    logger.info("="*80)
    logger.info("开始执行工作流...")
    logger.info("="*80)
    logger.info("")
    
    # 加载配置
    config = get_config()
    claude_config = config.get_ai_client_config("claude_code")
    claude_config["api_key"] = api_key
    
    # 创建客户端和编排器
    try:
        client = ClaudeCodeClient(claude_config)
        orchestrator = WorkflowOrchestrator(client=client)
    except Exception as e:
        logger.error(f"初始化失败: {e}", exc_info=True)
        sys.exit(1)
    
    # 执行工作流
    start_time = time.time()
    
    try:
        result = orchestrator.execute_workflow(
            workflow_name=workflow_name,
            requirement=requirement,
            project_path=project_path,
            dry_run=False
        )
    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("用户中断执行")
        sys.exit(130)
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        sys.exit(1)
    
    duration = time.time() - start_time
    
    # 显示结果
    logger.info("")
    logger.info("="*80)
    logger.info("执行结果")
    logger.info("="*80)
    logger.info(f"工作流: {result['workflow']}")
    logger.info(f"状态: {result['status']}")
    logger.info(f"总轮数: {result['total_iterations']}")
    logger.info(f"总耗时: {duration:.1f} 秒")
    logger.info("")
    
    # 各阶段详情
    for i, phase in enumerate(result['phases'], 1):
        status_icon = "✅" if phase.get('success') else "❌"
        logger.info(f"{status_icon} 阶段 {i}: {phase.get('phase', 'unknown')}")
        logger.info(f"   Agent: {phase.get('agent', 'unknown')}")
        logger.info(f"   轮数: {phase.get('iterations', 0)}, 耗时: {phase.get('duration', 0):.1f}秒")
        if not phase.get('success'):
            logger.error(f"   错误: {phase.get('error', '未知')}")
        logger.info("")
    
    # 检查生成的文件
    if result['success']:
        logger.info("检查生成的文件:")
        expected_files = [
            "Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.h",
            "Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.cpp"
        ]
        
        for file_path in expected_files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                logger.info(f"  ✅ {file_path} ({size} bytes)")
            else:
                logger.warning(f"  ⚠️  {file_path} (未找到)")
        
        logger.info("")
        logger.info("阶段输出文件:")
        phase_dir = Path(project_path) / ".claude" / "phases"
        if phase_dir.exists():
            for phase_file in sorted(phase_dir.glob("*.md")):
                size = phase_file.stat().st_size
                logger.info(f"  ✅ {phase_file.name} ({size} bytes)")
        else:
            logger.warning(f"  ⚠️  阶段输出目录不存在: {phase_dir}")
    
    logger.info("")
    logger.info("="*80)
    if result['success']:
        logger.info("✅ 工作流执行成功")
        logger.info("="*80)
        sys.exit(0)
    else:
        logger.error(f"❌ 工作流执行失败: {result.get('error')}")
        logger.info("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()

