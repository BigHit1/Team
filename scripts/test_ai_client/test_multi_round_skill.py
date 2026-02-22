"""
测试多轮对话协议 Skill
"""

import subprocess
import sys
import os
import re
import yaml
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_status(output: str):
    """解析状态块"""
    pattern = r'---TASK_STATUS---(.*?)---END_STATUS---'
    match = re.search(pattern, output, re.DOTALL)
    
    if not match:
        return None
    
    status_text = match.group(1).strip()
    
    try:
        status_dict = yaml.safe_load(status_text)
        return status_dict
    except:
        return None


def test_simple_task():
    """测试 1: 简单任务"""
    print("\n" + "="*60)
    print("测试 1: 简单任务（应该一轮完成）")
    print("="*60)
    
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://synai996.space/"
    env["ANTHROPIC_AUTH_TOKEN"] = "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o"
    
    requirement = """请使用多轮对话任务协议（增强版）。

任务：创建一个简单的 Python 函数 hello_world()，打印 "Hello, World!"
"""
    
    cmd = [
        "claude",
        "--add-dir", str(project_root),
        "--permission-mode", "bypassPermissions",
        "--print",
        requirement
    ]
    
    print(f"\n执行命令...")
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        shell=True,
        timeout=60
    )
    
    print("\n响应:")
    print(result.stdout)
    
    # 解析状态
    status = parse_status(result.stdout)
    
    if status:
        print("\n" + "="*60)
        print("状态解析结果:")
        print("="*60)
        print(f"状态: {status.get('status')}")
        print(f"原因: {status.get('reason')}")
        print(f"信心: {status.get('confidence', 'N/A')}")
        
        if status.get('status') == 'completed':
            print("✓ 测试通过 - 任务标记为完成")
            return True
        else:
            print(f"⚠ 状态不是 completed: {status.get('status')}")
            return False
    else:
        print("✗ 未找到状态块")
        return False


def test_complex_task():
    """测试 2: 复杂任务（应该多轮）"""
    print("\n" + "="*60)
    print("测试 2: 复杂任务（应该需要多轮）")
    print("="*60)
    
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://synai996.space/"
    env["ANTHROPIC_AUTH_TOKEN"] = "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o"
    
    requirement = """请使用多轮对话任务协议（增强版）。

任务：分析 ai_model_layer 目录的代码结构，包括：
1. 列出所有主要的类
2. 说明每个类的功能
3. 分析类之间的关系
4. 生成一个架构图（文本形式）
"""
    
    cmd = [
        "claude",
        "--add-dir", str(project_root),
        "--permission-mode", "bypassPermissions",
        "--print",
        requirement
    ]
    
    print(f"\n执行命令...")
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        shell=True,
        timeout=120
    )
    
    print("\n响应:")
    print(result.stdout)
    
    # 解析状态
    status = parse_status(result.stdout)
    
    if status:
        print("\n" + "="*60)
        print("状态解析结果:")
        print("="*60)
        print(f"状态: {status.get('status')}")
        print(f"原因: {status.get('reason')}")
        
        if status.get('status') in ['continue', 'completed', 'partial']:
            print("✓ 测试通过 - 状态合理")
            
            if status.get('status') == 'continue':
                print(f"进度: {status.get('progress', 0)*100:.1f}%")
                print(f"下一步: {status.get('next_part')}")
            
            return True
        else:
            print(f"⚠ 意外状态: {status.get('status')}")
            return False
    else:
        print("✗ 未找到状态块")
        return False


def test_need_decision():
    """测试 3: 需要决策的任务"""
    print("\n" + "="*60)
    print("测试 3: 需要决策的任务（应该返回 need_human）")
    print("="*60)
    
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://synai996.space/"
    env["ANTHROPIC_AUTH_TOKEN"] = "sk-ZFV2H6pQOf6sfC2EYGi8dqfMMQauY4652eDWMzAGsVAoyP8o"
    
    requirement = """请使用多轮对话任务协议（增强版）。

任务：为项目选择一个日志系统。有多种选择，请给出建议并等待我的决定。
"""
    
    cmd = [
        "claude",
        "--add-dir", str(project_root),
        "--permission-mode", "bypassPermissions",
        "--print",
        requirement
    ]
    
    print(f"\n执行命令...")
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        shell=True,
        timeout=60
    )
    
    print("\n响应:")
    print(result.stdout)
    
    # 解析状态
    status = parse_status(result.stdout)
    
    if status:
        print("\n" + "="*60)
        print("状态解析结果:")
        print("="*60)
        print(f"状态: {status.get('status')}")
        print(f"原因: {status.get('reason')}")
        
        if status.get('status') == 'need_human':
            print("✓ 测试通过 - 正确识别需要人类决策")
            print(f"介入类型: {status.get('intervention_type')}")
            print(f"优先级: {status.get('priority')}")
            
            if status.get('options'):
                print("选项:")
                for opt in status.get('options', []):
                    print(f"  - {opt}")
            
            return True
        else:
            print(f"⚠ 期望 need_human，实际: {status.get('status')}")
            return False
    else:
        print("✗ 未找到状态块")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("多轮对话协议 Skill 测试套件")
    print("="*60)
    
    results = []
    
    # 测试 1
    try:
        result1 = test_simple_task()
        results.append(("简单任务", result1))
    except Exception as e:
        print(f"\n测试 1 失败: {e}")
        results.append(("简单任务", False))
    
    # 测试 2
    try:
        result2 = test_complex_task()
        results.append(("复杂任务", result2))
    except Exception as e:
        print(f"\n测试 2 失败: {e}")
        results.append(("复杂任务", False))
    
    # 测试 3
    try:
        result3 = test_need_decision()
        results.append(("需要决策", result3))
    except Exception as e:
        print(f"\n测试 3 失败: {e}")
        results.append(("需要决策", False))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\n总计: {passed}/{total} 通过")
    print("="*60)
    
    return all(s for _, s in results)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

