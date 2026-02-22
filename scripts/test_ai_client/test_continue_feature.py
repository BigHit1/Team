"""
测试多轮对话的 --continue 功能
"""

import sys
from pathlib import Path

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


def test_multi_round_with_continue():
    """测试多轮对话（应该使用 --continue）"""
    logger.info("="*60)
    logger.info("测试多轮对话 --continue 功能")
    logger.info("="*60)
    
    config = {
        "api_key": "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o",
        "api_base_url": "https://synai996.space/",
        "model": "opus",
        "timeout": 300,
        "max_iterations": 3,  # 测试多轮
        "auto_continue": True,
        "index_directories": []
    }
    
    client = ClaudeCodeClient(config)
    
    # 一个需要多轮的任务
    requirement = """
    创建一个完整的武器系统，包括：
    1. 武器基类 WeaponBase
    2. 步枪类 Rifle
    3. 弹药组件 AmmoComponent
    
    每个类都要有详细的注释和基本功能。
    """
    
    result = client.execute_multi_round_task(
        requirement=requirement,
        project_path=str(project_root)
    )
    
    logger.info("="*60)
    logger.info("测试结果:")
    logger.info("="*60)
    logger.info(f"成功: {result['success']}")
    logger.info(f"总轮数: {result['iterations']}")
    logger.info(f"总耗时: {result['duration']:.1f}秒")
    logger.info(f"最终状态: {result.get('final_status')}")
    
    if result.get('status_block'):
        sb = result['status_block']
        logger.info(f"信心: {sb.confidence:.0%}")
        logger.info(f"修改文件: {len(sb.files_modified)} 个")
        
        if sb.files_modified:
            logger.info("修改的文件:")
            for f in sb.files_modified[:5]:
                logger.info(f"  - {f}")
    
    # 验证是否使用了 --continue
    logger.info("="*60)
    logger.info("命令验证:")
    logger.info("="*60)
    
    if result['iterations'] > 1:
        logger.info(f"执行了 {result['iterations']} 轮对话")
        logger.info(f"第 2-{result['iterations']} 轮应该使用了 --continue 参数")
    else:
        logger.warning(f"只执行了 1 轮，未测试 --continue")
    
    return result['success']


def test_simple_task_single_round():
    """测试简单任务（应该一轮完成，不使用 --continue）"""
    logger.info("="*60)
    logger.info("测试简单任务（一轮完成）")
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
    
    requirement = "创建一个简单的 Python 函数 add(a, b)，返回 a + b"
    
    result = client.execute_multi_round_task(
        requirement=requirement,
        project_path=str(project_root)
    )
    
    logger.info("="*60)
    logger.info("测试结果:")
    logger.info("="*60)
    logger.info(f"成功: {result['success']}")
    logger.info(f"轮数: {result['iterations']}")
    logger.info(f"状态: {result.get('final_status')}")
    
    if result['iterations'] == 1:
        logger.info("简单任务一轮完成，符合预期")
    else:
        logger.warning(f"简单任务用了 {result['iterations']} 轮")
    
    return result['success']


def main():
    """运行所有测试"""
    logger.info("="*60)
    logger.info("多轮对话 --continue 功能测试")
    logger.info("="*60)
    
    results = []
    
    # 测试 1: 简单任务
    try:
        result1 = test_simple_task_single_round()
        results.append(("简单任务（一轮）", result1))
    except Exception as e:
        logger.error(f"测试 1 失败: {e}", exc_info=True)
        results.append(("简单任务（一轮）", False))
    
    # 测试 2: 多轮任务
    try:
        result2 = test_multi_round_with_continue()
        results.append(("多轮任务（--continue）", result2))
    except Exception as e:
        logger.error(f"测试 2 失败: {e}", exc_info=True)
        results.append(("多轮任务（--continue）", False))
    
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

