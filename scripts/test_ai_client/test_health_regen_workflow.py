"""
测试生命恢复技能工作流
完整测试从需求到代码生成的闭环流程
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.utils.logger import setup_logging, get_logger
from ai_model_layer.config import load_config

# 初始化日志系统
setup_logging(
    log_dir="logs",
    console_level="INFO",
    file_level="DEBUG",
    enable_json=True,
    enable_color=True
)

# 获取日志器
logger = get_logger(__name__)


def load_requirement(requirement_file: str) -> str:
    """加载需求文档"""
    req_path = Path(__file__).parent.parent / requirement_file
    
    if not req_path.exists():
        raise FileNotFoundError(f"需求文件不存在: {req_path}")
    
    logger.info(f"加载需求文档: {req_path}")
    return req_path.read_text(encoding='utf-8')


def test_dry_run():
    """测试 1: 干运行模式（验证配置）"""
    logger.info("="*80)
    logger.info("测试 1: 干运行模式 - 验证工作流配置")
    logger.info("="*80)
    
    try:
        # 加载需求
        requirement = load_requirement("requirements/examples/add_health_regen_ability.md")
        
        # 创建编排器（不需要 client）
        orchestrator = WorkflowOrchestrator()
        
        # 执行干运行
        logger.info("开始干运行...")
        result = orchestrator.execute_workflow(
            workflow_name="standard",
            requirement=requirement,
            dry_run=True
        )
        
        # 验证结果
        logger.info("干运行结果:")
        logger.info(f"  工作流: {result['workflow']}")
        logger.info(f"  状态: {result['status']}")
        logger.info(f"  成功: {result['success']}")
        logger.info(f"  阶段数: {len(result['phases'])}")
        
        for i, phase in enumerate(result['phases'], 1):
            logger.info(f"  阶段 {i}: {phase['phase']}")
            logger.info(f"    Agent: {phase['agent']}")
            logger.info(f"    状态: {phase['status']}")
            logger.info(f"    成功: {phase['success']}")
        
        if result['success']:
            logger.info("✅ 干运行测试通过")
            return True
        else:
            logger.error(f"❌ 干运行测试失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 干运行测试异常: {e}", exc_info=True)
        return False


def test_quick_workflow(project_path: str):
    """测试 2: 快速工作流（实际执行）"""
    logger.info("="*80)
    logger.info("测试 2: 快速工作流 - 实际执行代码生成")
    logger.info("="*80)
    
    try:
        # 加载配置
        config = load_config()
        claude_config = config.get("ai_client", {}).get("claude_code", {})
        
        # 检查 API Key
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
        if not api_key:
            logger.warning("⚠️  未设置 API Key，跳过实际执行测试")
            logger.info("提示: 设置环境变量 ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN")
            return None
        
        claude_config["api_key"] = api_key
        
        # 创建客户端
        logger.info("初始化 Claude Code 客户端...")
        client = ClaudeCodeClient(claude_config)
        
        # 加载需求
        requirement = load_requirement("requirements/examples/add_health_regen_ability.md")
        
        # 创建编排器
        orchestrator = WorkflowOrchestrator(client=client)
        
        # 执行快速工作流（只有 Plan + Code，跳过 Architect 和 Review）
        logger.info("开始执行快速工作流...")
        logger.info(f"项目路径: {project_path}")
        
        start_time = time.time()
        
        result = orchestrator.execute_workflow(
            workflow_name="quick",
            requirement=requirement,
            project_path=project_path,
            dry_run=False
        )
        
        duration = time.time() - start_time
        
        # 显示结果
        logger.info("="*80)
        logger.info("工作流执行结果:")
        logger.info(f"  工作流: {result['workflow']}")
        logger.info(f"  状态: {result['status']}")
        logger.info(f"  成功: {result['success']}")
        logger.info(f"  总轮数: {result['total_iterations']}")
        logger.info(f"  总耗时: {duration:.1f} 秒")
        logger.info("="*80)
        
        # 显示各阶段结果
        for i, phase in enumerate(result['phases'], 1):
            logger.info(f"阶段 {i}: {phase.get('phase', 'unknown')}")
            logger.info(f"  Agent: {phase.get('agent', 'unknown')}")
            logger.info(f"  状态: {phase.get('status', 'unknown')}")
            logger.info(f"  轮数: {phase.get('iterations', 0)}")
            logger.info(f"  耗时: {phase.get('duration', 0):.1f} 秒")
            
            if not phase.get('success'):
                logger.error(f"  错误: {phase.get('error', '未知错误')}")
        
        if result['success']:
            logger.info("✅ 快速工作流测试通过")
            
            # 检查生成的文件
            logger.info("检查生成的文件...")
            check_generated_files(project_path)
            
            return True
        else:
            logger.error(f"❌ 快速工作流测试失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 快速工作流测试异常: {e}", exc_info=True)
        return False


def test_standard_workflow(project_path: str):
    """测试 3: 标准工作流（完整流程）"""
    logger.info("="*80)
    logger.info("测试 3: 标准工作流 - 完整的 Plan → Architect → Code → Review")
    logger.info("="*80)
    
    try:
        # 加载配置
        config = load_config()
        claude_config = config.get("ai_client", {}).get("claude_code", {})
        
        # 检查 API Key
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
        if not api_key:
            logger.warning("⚠️  未设置 API Key，跳过标准工作流测试")
            return None
        
        claude_config["api_key"] = api_key
        
        # 创建客户端
        logger.info("初始化 Claude Code 客户端...")
        client = ClaudeCodeClient(claude_config)
        
        # 加载需求
        requirement = load_requirement("requirements/examples/add_health_regen_ability.md")
        
        # 创建编排器
        orchestrator = WorkflowOrchestrator(client=client)
        
        # 执行标准工作流
        logger.info("开始执行标准工作流...")
        logger.info(f"项目路径: {project_path}")
        
        start_time = time.time()
        
        result = orchestrator.execute_workflow(
            workflow_name="standard",
            requirement=requirement,
            project_path=project_path,
            dry_run=False
        )
        
        duration = time.time() - start_time
        
        # 显示结果
        logger.info("="*80)
        logger.info("工作流执行结果:")
        logger.info(f"  工作流: {result['workflow']}")
        logger.info(f"  状态: {result['status']}")
        logger.info(f"  成功: {result['success']}")
        logger.info(f"  总轮数: {result['total_iterations']}")
        logger.info(f"  总耗时: {duration:.1f} 秒")
        logger.info("="*80)
        
        # 显示各阶段结果
        for i, phase in enumerate(result['phases'], 1):
            logger.info(f"阶段 {i}: {phase.get('phase', 'unknown')}")
            logger.info(f"  Agent: {phase.get('agent', 'unknown')}")
            logger.info(f"  状态: {phase.get('status', 'unknown')}")
            logger.info(f"  轮数: {phase.get('iterations', 0)}")
            logger.info(f"  耗时: {phase.get('duration', 0):.1f} 秒")
            
            if not phase.get('success'):
                logger.error(f"  错误: {phase.get('error', '未知错误')}")
        
        if result['success']:
            logger.info("✅ 标准工作流测试通过")
            
            # 检查生成的文件
            logger.info("检查生成的文件...")
            check_generated_files(project_path)
            check_phase_outputs(project_path)
            
            return True
        else:
            logger.error(f"❌ 标准工作流测试失败: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 标准工作流测试异常: {e}", exc_info=True)
        return False


def check_generated_files(project_path: str):
    """检查生成的代码文件"""
    expected_files = [
        "Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.h",
        "Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.cpp"
    ]
    
    project_root = Path(project_path)
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            logger.info(f"  ✅ {file_path} ({size} bytes)")
        else:
            logger.warning(f"  ⚠️  {file_path} (未找到)")


def check_phase_outputs(project_path: str):
    """检查阶段输出文件"""
    phase_outputs = [
        ".claude/phases/plan.md",
        ".claude/phases/architecture.md",
        ".claude/phases/implementation.md",
        ".claude/phases/review.md"
    ]
    
    project_root = Path(project_path)
    
    logger.info("检查阶段输出文件...")
    for output_file in phase_outputs:
        full_path = project_root / output_file
        if full_path.exists():
            size = full_path.stat().st_size
            logger.info(f"  ✅ {output_file} ({size} bytes)")
        else:
            logger.warning(f"  ⚠️  {output_file} (未找到)")


def main():
    """主测试函数"""
    logger.info("="*80)
    logger.info("生命恢复技能工作流测试套件")
    logger.info("="*80)
    
    # 获取项目路径
    project_path = os.getenv("LYRA_PROJECT_PATH")
    
    if not project_path:
        logger.warning("⚠️  未设置 LYRA_PROJECT_PATH 环境变量")
        logger.info("提示: 设置环境变量指向 LyraStarterGame 项目路径")
        logger.info("示例: set LYRA_PROJECT_PATH=D:\\UE5Projects\\LyraStarterGame")
        logger.info("")
        logger.info("将只运行干运行测试...")
        project_path = None
    else:
        logger.info(f"项目路径: {project_path}")
        
        # 验证路径
        if not Path(project_path).exists():
            logger.error(f"❌ 项目路径不存在: {project_path}")
            sys.exit(1)
    
    logger.info("")
    
    # 测试计数
    tests_run = 0
    tests_passed = 0
    tests_failed = 0
    tests_skipped = 0
    
    # 测试 1: 干运行
    tests_run += 1
    if test_dry_run():
        tests_passed += 1
    else:
        tests_failed += 1
    
    logger.info("")
    
    # 测试 2: 快速工作流（需要项目路径）
    if project_path:
        tests_run += 1
        result = test_quick_workflow(project_path)
        if result is True:
            tests_passed += 1
        elif result is False:
            tests_failed += 1
        else:
            tests_skipped += 1
        
        logger.info("")
    
    # 测试 3: 标准工作流（需要项目路径，可选）
    if project_path:
        logger.info("是否运行标准工作流测试？（耗时较长，约 10-20 分钟）")
        logger.info("提示: 设置环境变量 RUN_FULL_TEST=1 自动运行")
        
        run_full = os.getenv("RUN_FULL_TEST") == "1"
        
        if run_full:
            tests_run += 1
            result = test_standard_workflow(project_path)
            if result is True:
                tests_passed += 1
            elif result is False:
                tests_failed += 1
            else:
                tests_skipped += 1
        else:
            logger.info("⏭️  跳过标准工作流测试")
            tests_skipped += 1
    
    # 总结
    logger.info("")
    logger.info("="*80)
    logger.info("测试总结")
    logger.info("="*80)
    logger.info(f"运行: {tests_run}")
    logger.info(f"通过: {tests_passed} ✅")
    logger.info(f"失败: {tests_failed} ❌")
    logger.info(f"跳过: {tests_skipped} ⏭️")
    logger.info("="*80)
    
    if tests_failed > 0:
        logger.error("部分测试失败")
        sys.exit(1)
    else:
        logger.info("所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()

