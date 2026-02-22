"""
测试标准工作流 - 生命恢复技能完整需求
使用 standard.yaml 执行完整的 Plan → Architect → Code → Review 流程
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.utils.logger import setup_logging, get_logger
from ai_model_layer.config import get_config

# 初始化日志系统
setup_logging(
    log_dir="logs",
    console_level="INFO",
    file_level="DEBUG",
    enable_json=False
)

logger = get_logger(__name__)


def load_requirement(requirement_file: str) -> str:
    """加载需求文档"""
    req_path = Path(__file__).parent.parent.parent / requirement_file
    
    if not req_path.exists():
        raise FileNotFoundError(f"需求文件不存在: {req_path}")
    
    logger.info(f"📄 加载需求文档: {req_path}")
    return req_path.read_text(encoding='utf-8')


def execute_standard_workflow(project_path: str):
    """执行标准工作流"""
    logger.info("="*80)
    logger.info("🚀 执行标准工作流")
    logger.info("="*80)
    
    try:
        # 加载配置
        config_manager = get_config()
        claude_config = config_manager.get_ai_client_config("claude_code")
        
        # 创建客户端
        logger.info("🔧 初始化 Claude Code 客户端...")
        client = ClaudeCodeClient(claude_config)
        
        # 加载需求
        requirement = load_requirement("requirements/examples/add_health_regen_ability.md")
        
        logger.info("📋 需求内容:")
        logger.info("-" * 80)
        # 显示需求摘要
        lines = requirement.split('\n')
        for line in lines[:15]:  # 显示前15行
            logger.info(f"  {line}")
        logger.info("  ...")
        logger.info("-" * 80)
        
        # 创建编排器
        orchestrator = WorkflowOrchestrator(client=client)
        
        # 执行标准工作流
        logger.info("⚙️  开始执行标准工作流...")
        logger.info(f"📁 项目路径: {project_path}")
        logger.info(f"📝 工作流: standard.yaml")
        logger.info("")
        
        start_time = time.time()
        
        result = orchestrator.execute_workflow(
            workflow_name="standard",
            requirement=requirement,
            project_path=project_path,
            dry_run=False
        )
        
        duration = time.time() - start_time
        
        # 显示结果
        logger.info("")
        logger.info("="*80)
        logger.info("📊 工作流执行结果")
        logger.info("="*80)
        logger.info(f"工作流: {result['workflow']}")
        logger.info(f"状态: {result['status']}")
        logger.info(f"成功: {'✅ 是' if result['success'] else '❌ 否'}")
        logger.info(f"总轮数: {result['total_iterations']}")
        logger.info(f"总耗时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
        logger.info("="*80)
        logger.info("")
        
        # 显示各阶段详情
        logger.info("📋 各阶段执行详情:")
        logger.info("-" * 80)
        
        for i, phase in enumerate(result['phases'], 1):
            phase_name = phase.get('phase', 'unknown')
            agent = phase.get('agent', 'unknown')
            status = phase.get('status', 'unknown')
            iterations = phase.get('iterations', 0)
            phase_duration = phase.get('duration', 0)
            success = phase.get('success', False)
            
            status_icon = "✅" if success else "❌"
            
            logger.info(f"{status_icon} 阶段 {i}: {phase_name}")
            logger.info(f"   Agent: {agent}")
            logger.info(f"   状态: {status}")
            logger.info(f"   轮数: {iterations}")
            logger.info(f"   耗时: {phase_duration:.1f} 秒")
            
            if not success:
                error = phase.get('error', '未知错误')
                logger.error(f"   错误: {error}")
            
            logger.info("")
        
        logger.info("-" * 80)
        
        # 检查生成的文件
        if result['success']:
            logger.info("")
            check_outputs(project_path)
            
            logger.info("")
            logger.info("="*80)
            logger.info("✅ 标准工作流执行成功！")
            logger.info("="*80)
            return True
        else:
            logger.error("")
            logger.error("="*80)
            logger.error(f"❌ 标准工作流执行失败: {result.get('error', '未知错误')}")
            logger.error("="*80)
            return False
            
    except Exception as e:
        logger.error(f"❌ 执行异常: {e}", exc_info=True)
        return False


def check_outputs(project_path: str):
    """检查输出文件"""
    logger.info("📂 检查生成的文件:")
    logger.info("-" * 80)
    
    project_root = Path(project_path)
    
    # 检查阶段输出文档
    phase_outputs = [
        (".claude/phases/plan.md", "规划文档"),
        (".claude/phases/architecture.md", "架构设计文档"),
        (".claude/phases/implementation.md", "实现文档"),
        (".claude/phases/review.md", "审查报告")
    ]
    
    logger.info("📄 阶段输出文档:")
    for output_file, desc in phase_outputs:
        full_path = project_root / output_file
        if full_path.exists():
            size = full_path.stat().st_size
            logger.info(f"  ✅ {desc}: {output_file} ({size:,} bytes)")
        else:
            logger.warning(f"  ⚠️  {desc}: {output_file} (未找到)")
    
    logger.info("")
    
    # 检查生成的代码文件
    expected_files = [
        ("Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.h", "头文件"),
        ("Source/LyraGame/AbilitySystem/Abilities/LyraGameplayAbility_HealthRegen.cpp", "实现文件")
    ]
    
    logger.info("💻 生成的代码文件:")
    for file_path, desc in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            logger.info(f"  ✅ {desc}: {file_path} ({size:,} bytes)")
        else:
            logger.warning(f"  ⚠️  {desc}: {file_path} (未找到)")
    
    logger.info("-" * 80)


def main():
    """主函数"""
    logger.info("")
    logger.info("="*80)
    logger.info("🎮 生命恢复技能 - 标准工作流测试")
    logger.info("="*80)
    logger.info("需求文件: requirements/examples/add_health_regen_ability.md")
    logger.info("工作流: standard.yaml (Plan → Architect → Code → Review)")
    logger.info("="*80)
    logger.info("")
    
    
    # 获取项目路径
    project_path = r"F:\UE5\LyraStarterGame"
    
    # 执行工作流
    success = execute_standard_workflow(project_path)
    
    logger.info("")
    
    if success:
        logger.info("🎉 测试完成！")
        sys.exit(0)
    else:
        logger.error("💥 测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()

