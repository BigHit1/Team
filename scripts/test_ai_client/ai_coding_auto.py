"""
自动化编码脚本 - 使用 Claude Code CLI
支持自动迭代和验证循环
"""

import argparse
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.config import get_config
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient


class CodeValidator:
    """代码验证器"""
    
    def __init__(self, project_path: str, config: Dict[str, Any]):
        self.project_path = Path(project_path)
        self.config = config
    
    def validate(self, output: str) -> bool:
        """
        验证代码是否完成
        
        验证策略：
        1. 检查是否有编译错误
        2. 检查是否生成了预期的文件
        3. 检查输出中是否包含完成标记
        
        Args:
            output: Claude Code 的输出
        
        Returns:
            True 表示任务完成，False 表示需要继续迭代
        """
        print("\n=== 开始验证 ===")
        
        # 策略 1: 检查输出中的完成标记
        if self._check_completion_markers(output):
            print("✓ 发现完成标记")
            return True
        
        # 策略 2: 检查是否有错误标记
        if self._check_error_markers(output):
            print("✗ 发现错误标记，需要继续迭代")
            return False
        
        # 策略 3: 尝试编译代码
        if self.config.get("validate_with_compile", False):
            if self._try_compile():
                print("✓ 编译成功")
                return True
            else:
                print("✗ 编译失败，需要继续迭代")
                return False
        
        # 策略 4: 检查文件变更
        if self._check_file_changes():
            print("✓ 检测到文件变更")
            # 如果有文件变更且没有错误，认为完成
            return not self._check_error_markers(output)
        
        # 默认：如果没有明确的错误，认为完成
        print("⚠ 无法明确判断，默认认为完成")
        return True
    
    def _check_completion_markers(self, output: str) -> bool:
        """检查完成标记"""
        completion_markers = [
            "任务完成",
            "Task completed",
            "Successfully",
            "Done",
            "✓",
            "已完成"
        ]
        
        output_lower = output.lower()
        return any(marker.lower() in output_lower for marker in completion_markers)
    
    def _check_error_markers(self, output: str) -> bool:
        """检查错误标记"""
        error_markers = [
            "error:",
            "错误:",
            "failed",
            "失败",
            "exception",
            "异常",
            "✗"
        ]
        
        output_lower = output.lower()
        return any(marker.lower() in output_lower for marker in error_markers)
    
    def _try_compile(self) -> bool:
        """尝试编译项目"""
        try:
            # 查找 UE5 编译脚本
            build_script = self.project_path / "Build.bat"
            
            if not build_script.exists():
                print("⚠ 未找到编译脚本，跳过编译验证")
                return True
            
            print("正在编译项目...")
            result = subprocess.run(
                [str(build_script)],
                cwd=str(self.project_path),
                capture_output=True,
                timeout=300,
                text=True
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⚠ 编译超时")
            return False
        except Exception as e:
            print(f"⚠ 编译检查失败: {e}")
            return True  # 编译检查失败不影响主流程
    
    def _check_file_changes(self) -> bool:
        """检查是否有文件变更（通过 Git）"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 如果有输出，说明有文件变更
            return bool(result.stdout.strip())
            
        except Exception as e:
            print(f"⚠ Git 检查失败: {e}")
            return False


def load_requirement(requirement_path: str) -> str:
    """加载需求文档"""
    path = Path(requirement_path)
    
    if not path.exists():
        raise FileNotFoundError(f"需求文件不存在: {requirement_path}")
    
    return path.read_text(encoding='utf-8')


def save_result(result: Dict[str, Any], output_path: str):
    """保存结果"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="自动化编码脚本 - 使用 Claude Code CLI"
    )
    
    parser.add_argument(
        "--requirement",
        required=True,
        help="需求文档路径"
    )
    
    parser.add_argument(
        "--project-path",
        required=True,
        help="UE5 项目路径"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="最大迭代次数（默认: 5）"
    )
    
    parser.add_argument(
        "--output",
        default="output/coding_result.json",
        help="结果输出路径"
    )
    
    parser.add_argument(
        "--validate-compile",
        action="store_true",
        help="是否通过编译验证代码"
    )
    
    parser.add_argument(
        "--config-dir",
        help="配置文件目录"
    )
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*60)
        print("自动化编码脚本 - Claude Code CLI")
        print("="*60)
        
        # 加载配置
        print("\n1. 加载配置...")
        config = get_config(args.config_dir)
        client_config = config.get_ai_client_config("claude_code")
        
        # 设置最大迭代次数
        client_config["max_iterations"] = args.max_iterations
        
        # 创建客户端
        print("2. 初始化 Claude Code CLI 客户端...")
        client = ClaudeCodeClient(client_config)
        
        # 加载需求
        print(f"3. 加载需求文档: {args.requirement}")
        requirement = load_requirement(args.requirement)
        print(f"   需求长度: {len(requirement)} 字符")
        
        # 创建验证器
        print("4. 创建代码验证器...")
        validator = CodeValidator(
            args.project_path,
            {"validate_with_compile": args.validate_compile}
        )
        
        # 开始自动迭代
        print("\n5. 开始自动化迭代编码...")
        result = client.auto_iterate(
            requirement=requirement,
            project_path=args.project_path,
            validation_func=validator.validate,
            max_iterations=args.max_iterations
        )
        
        # 保存结果
        print("\n6. 保存结果...")
        save_result(result, args.output)
        
        # 输出总结
        print("\n" + "="*60)
        print("执行总结")
        print("="*60)
        print(f"状态: {'✓ 成功' if result['success'] else '✗ 失败'}")
        print(f"迭代次数: {result['iterations']}")
        
        if result['success']:
            print(f"最终输出长度: {len(result.get('final_output', ''))} 字符")
        else:
            print(f"错误信息: {result.get('error', '未知错误')}")
        
        print("="*60 + "\n")
        
        # 返回退出码
        sys.exit(0 if result['success'] else 1)
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



