"""
测试新的 ClaudeCodeClient（基于多轮对话协议）
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
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


def test_simple_task():
    """测试 1: 简单任务（应该一轮完成）"""
    logger.info("="*60)
    logger.info("测试 1: 简单任务")
    logger.info("="*60)
    
    config = {
        "api_key": "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o",
        "api_base_url": "https://synai996.space/",
        "model": "opus",
        "timeout": 120,
        "max_iterations": 5,
        "auto_continue": True,
        "index_directories": []
    }
    
    client = ClaudeCodeClient(config)
    
    requirement = "创建一个简单的 Python 函数 hello_world()，打印 'Hello, World!'"
    
    result = client.execute_multi_round_task(
        requirement=requirement,
        project_path=str(project_root)
    )
    
    logger.info("="*60)
    logger.info("测试结果:")
    logger.info("="*60)
    logger.info(f"成功: {result['success']}")
    logger.info(f"轮数: {result['iterations']}")
    logger.info(f"耗时: {result['duration']:.1f}秒")
    logger.info(f"最终状态: {result.get('final_status')}")
    
    if result.get('status_block'):
        sb = result['status_block']
        logger.info(f"信心: {sb.confidence:.0%}")
        logger.info(f"原因: {sb.reason}")
    
    return result['success']


def test_lyra_weapon_analysis():
    """测试 2: 分析 Lyra 武器系统（复杂任务）"""
    logger.info("="*60)
    logger.info("测试 2: 分析 Lyra 武器系统")
    logger.info("="*60)
    
    config = {
        "api_key": "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o",
        "api_base_url": "https://synai996.space/",
        "model": "opus",
        "timeout": 300,
        "max_iterations": 10,
        "auto_continue": True,
        "index_directories": ["F:/UE5/LyraStarterGame"]
    }
    
    client = ClaudeCodeClient(config)
    
    requirement = "分析当前项目中的Lyra项目的武器系统的架构，并写入doc/weapon.md"
    
    result = client.execute_multi_round_task(
        requirement=requirement,
        project_path="F:/UE5/LyraStarterGame"
    )
    
    logger.info("="*60)
    logger.info("测试结果:")
    logger.info("="*60)
    logger.info(f"成功: {result['success']}")
    logger.info(f"轮数: {result['iterations']}")
    logger.info(f"耗时: {result['duration']:.1f}秒")
    logger.info(f"最终状态: {result.get('final_status')}")
    
    if result.get('status_block'):
        sb = result['status_block']
        logger.info(f"信心: {sb.confidence:.0%}")
        logger.info(f"修改文件: {len(sb.files_modified)} 个")
        if sb.files_modified:
            for f in sb.files_modified[:5]:
                logger.info(f"  - {f}")
    
    return result['success']


def test_generate_code_api():
    """测试 3: 使用 generate_code API"""
    logger.info("="*60)
    logger.info("测试 3: generate_code API")
    logger.info("="*60)
    
    config = {
        "api_key": "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o",
        "api_base_url": "https://synai996.space/",
        "model": "opus",
        "timeout": 120,
        "max_iterations": 5,
        "auto_continue": True
    }
    
    client = ClaudeCodeClient(config)
    
    response = client.generate_code(
        requirement="创建一个计算斐波那契数列的函数",
        context={"project_path": str(project_root)}
    )
    
    logger.info("="*60)
    logger.info("测试结果:")
    logger.info("="*60)
    logger.info(f"模型: {response.model}")
    logger.info(f"完成原因: {response.finish_reason}")
    logger.info(f"轮数: {response.metadata.get('iterations')}")
    logger.info(f"耗时: {response.metadata.get('duration', 0):.1f}秒")
    logger.info("输出预览:")
    logger.debug(response.content[:500])
    
    return response.finish_reason == "complete"


def main():
    """运行所有测试"""
    logger.info("="*60)
    logger.info("ClaudeCodeClient 测试套件（多轮对话协议）")
    logger.info("="*60)
    
    results = []
    
    # 测试 1: 简单任务
    try:
        result1 = test_simple_task()
        results.append(("简单任务", result1))
    except Exception as e:
        logger.error(f"测试 1 失败: {e}", exc_info=True)
        results.append(("简单任务", False))
    
    # 测试 2: Lyra 武器分析（可选，需要 Lyra 项目）
    try:
        if Path("F:/UE5/LyraStarterGame").exists():
            result2 = test_lyra_weapon_analysis()
            results.append(("Lyra 武器分析", result2))
        else:
            logger.warning("跳过测试 2: Lyra 项目不存在")
    except Exception as e:
        logger.error(f"测试 2 失败: {e}", exc_info=True)
        results.append(("Lyra 武器分析", False))
    
    # 测试 3: generate_code API
    try:
        result3 = test_generate_code_api()
        results.append(("generate_code API", result3))
    except Exception as e:
        logger.error(f"测试 3 失败: {e}", exc_info=True)
        results.append(("generate_code API", False))
    
    # 总结
    logger.info("="*60)
    logger.info("测试总结")
    logger.info("="*60)
    
    for name, success in results:
        if success:
            logger.info(f"{name}: 通过")
        else:
            logger.error(f"{name}: 失败")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    logger.info(f"总计: {passed}/{total} 通过")
    logger.info("="*60)
    
    return all(s for _, s in results)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("用户中断")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"错误: {e}", exc_info=True)
        sys.exit(1)

