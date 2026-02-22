"""
Claude Code CLI 客户端（基于多轮对话协议）
通过 Claude Code CLI 和 multi-round-protocol skill 进行自动化编码
实现原子对话的 自动化的多轮对话
"""

import subprocess
import os
import re
import yaml
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..ai_client import AIClient, AIMessage, AIResponse
from ..utils.git_wrapper import get_git_wrapper
from ..utils.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


class TaskStatus(Enum):
    """任务状态（对应 multi-round-protocol）"""
    COMPLETED = "completed"      # 已完成
    NEED_HUMAN = "need_human"    # 需要人类介入
    CONTINUE = "continue"        # 需要继续
    ERROR = "error"              # 错误
    WAITING = "waiting"          # 等待中
    PARTIAL = "partial"          # 部分完成
    UNKNOWN = "unknown"          # 未知（无状态块）


@dataclass
class StatusBlock:
    """状态块数据"""
    status: TaskStatus
    reason: str
    confidence: float = 0.0
    progress: float = 0.0
    next_part: str = ""
    error_message: str = ""
    intervention_type: str = ""
    priority: str = ""
    files_modified: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.files_modified is None:
            self.files_modified = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ClaudeCodeTask:
    """Claude Code 任务"""
    task_id: str
    requirement: str
    project_path: str
    iteration: int = 0
    output: str = ""
    status_block: Optional[StatusBlock] = None
    start_time: float = 0
    end_time: float = 0
    
    def duration(self) -> float:
        """获取任务执行时长"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        elif self.start_time > 0:
            return time.time() - self.start_time
        return 0


class ClaudeCodeClient(AIClient):
    """Claude Code CLI 客户端 - 基于多轮对话协议"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 只从config字典读取，不读取环境变量
        self.api_key = config.get("api_key")
        self.api_base_url = config.get("api_base_url")
        self.cli_path = config.get("cli_path", "claude")
        self.max_iterations = config.get("max_iterations", 10)
        self.auto_continue = config.get("auto_continue", True)
        self.index_directories = config.get("index_directories", [])
        
        logger.info("初始化 Claude Code 客户端", extra={
            "cli_path": self.cli_path,
            "model": self.model,
            "max_iterations": self.max_iterations,
            "auto_continue": self.auto_continue,
            "index_dirs_count": len(self.index_directories)
        })
        
        # 任务历史
        self.tasks: Dict[str, ClaudeCodeTask] = {}
        self.task_counter = 0
        
        # 初始化
        self.git_wrapper = get_git_wrapper()
        self._setup_environment()
        
        if not self._check_cli_available():
            logger.critical(f"Claude Code CLI 不可用: {self.cli_path}")
            raise RuntimeError(f"Claude Code CLI 不可用: {self.cli_path}")
        
        logger.info("Claude Code 客户端初始化完成")
    
    def _setup_environment(self):
        """设置环境变量"""
        env_vars_set = []
        
        # Git Bash
        try:
            if self.git_wrapper.is_bash_available():
                bash_path = self.git_wrapper.get_bash_path()
                os.environ["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path
                env_vars_set.append("CLAUDE_CODE_GIT_BASH_PATH")
                logger.debug(f"Git Bash 路径已设置: {bash_path}")
        except Exception as e:
            logger.warning(f"无法设置 Git Bash 路径: {e}")
        
        # API 配置
        if self.api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            os.environ["ANTHROPIC_AUTH_TOKEN"] = self.api_key
            env_vars_set.extend(["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"])
            logger.debug("API 认证信息已设置")
        else:
            logger.warning("未提供 API Key，可能导致认证失败")
        
        if self.api_base_url:
            os.environ["ANTHROPIC_BASE_URL"] = self.api_base_url
            env_vars_set.append("ANTHROPIC_BASE_URL")
            logger.debug(f"API Base URL 已设置: {self.api_base_url}")
        
        logger.debug(f"环境变量设置完成", extra={
            "env_vars_count": len(env_vars_set),
            "env_vars": env_vars_set
        })
    
    def _check_cli_available(self) -> bool:
        """检查 CLI 是否可用"""
        logger.debug(f"检查 CLI 可用性: {self.cli_path}")
        
        try:
            if os.name == 'nt':
                result = subprocess.run(
                    ["powershell", "-Command", f"{self.cli_path} --version"],
                    capture_output=True,
                    timeout=10,
                    text=True
                )
            else:
                result = subprocess.run(
                    [self.cli_path, "--version"],
                    capture_output=True,
                    timeout=10,
                    text=True
                )
            
            available = result.returncode == 0
            
            if available:
                version = result.stdout.strip()
                logger.info("Claude Code CLI 可用", extra={
                    "cli_path": self.cli_path,
                    "version": version,
                    "platform": os.name
                })
            else:
                logger.error("Claude Code CLI 不可用", extra={
                    "cli_path": self.cli_path,
                    "return_code": result.returncode,
                    "stderr": result.stderr[:200] if result.stderr else None
                })
            
            return available
            
        except subprocess.TimeoutExpired:
            logger.error("CLI 检查超时", extra={
                "cli_path": self.cli_path,
                "timeout_seconds": 10
            })
            return False
        except Exception as e:
            logger.error("CLI 检查失败", exc_info=True, extra={
                "cli_path": self.cli_path,
                "error_type": type(e).__name__
            })
            return False
    
    def generate_code(
        self,
        requirement: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIResponse:
        """
        生成代码（使用多轮对话协议）
        
        Args:
            requirement: 需求描述
            context: 上下文信息
            **kwargs: 其他参数
        
        Returns:
            AI 响应
        """
        project_path = context.get("project_path", ".") if context else "."
        
        # 执行多轮任务
        result = self.execute_multi_round_task(requirement, project_path)
        
        return AIResponse(
            content=result["final_output"],
            model=self.model,
            tokens_used=0,
            finish_reason="complete" if result["success"] else "error",
            metadata={
                "task_id": result["task_id"],
                "iterations": result["iterations"],
                "duration": result["duration"],
                "status": result.get("final_status", "unknown")
            }
        )
    
    def execute_multi_round_task(
        self,
        requirement: str,
        project_path: str
    ) -> Dict[str, Any]:
        """
        执行多轮对话任务
        
        Args:
            requirement: 需求描述
            project_path: 项目路径
        
        Returns:
            任务结果
        """
        # 生成任务 ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        # 创建带上下文的日志器
        task_logger = get_logger(__name__, context={
            "task_id": task_id,
            "project": Path(project_path).name
        })
        
        task_logger.info("="*60)
        task_logger.info("开始多轮对话任务")
        task_logger.info("="*60)
        task_logger.info(f"任务ID: {task_id}")
        task_logger.info(f"项目路径: {project_path}")
        task_logger.info(f"项目名称: {Path(project_path).name}")
        task_logger.info(f"最大迭代次数: {self.max_iterations}")
        task_logger.info(f"自动继续: {self.auto_continue}")
        task_logger.info(f"需求描述 ({len(requirement)} 字符):")
        task_logger.info("-"*60)
        task_logger.info("-"*60)
        task_logger.info("="*60)
        
        iteration = 0
        all_outputs = []
        start_time = time.time()
        
        while iteration < self.max_iterations:
            iteration += 1
            round_start = time.time()
            
            task_logger.info("="*60)
            task_logger.info(f"第 {iteration}/{self.max_iterations} 轮开始")
            task_logger.info("="*60)
            
            # 执行单轮任务
            task = self._execute_single_round(
                requirement,
                project_path,
                task_id,
                iteration
            )
            
            all_outputs.append(task.output)
            
            # 解析状态块
            status_block = self._parse_status_block(task.output)
            task.status_block = status_block
            
            round_duration = time.time() - round_start
            
            task_logger.info(f"第 {iteration} 轮完成，耗时: {round_duration:.2f}秒")
            
            if not status_block:
                task_logger.warning("="*60)
                task_logger.warning("未找到状态块")
                task_logger.warning("="*60)
                task_logger.warning("任务可能未使用多轮协议")
                task_logger.warning(f"迭代次数: {iteration}")
                task_logger.warning(f"本轮耗时: {round_duration:.2f}秒")
                task_logger.warning("="*60)
                return {
                    "success": False,
                    "task_id": task_id,
                    "iterations": iteration,
                    "duration": time.time() - start_time,
                    "final_output": task.output,
                    "error": "未找到状态块"
                }
            
            # 根据状态决定下一步
            if status_block.status == TaskStatus.COMPLETED:
                duration = time.time() - start_time
                task_logger.info("="*60)
                task_logger.info("任务成功完成")
                task_logger.info("="*60)
                task_logger.info(f"置信度: {status_block.confidence}")
                task_logger.info(f"总迭代次数: {iteration}")
                task_logger.info(f"总耗时: {duration:.2f}秒")
                task_logger.info(f"平均每轮耗时: {duration / iteration:.2f}秒")
                task_logger.info(f"修改的文件数: {len(status_block.files_modified)}")
                if status_block.files_modified:
                    task_logger.info("修改的文件:")
                    for f in status_block.files_modified:
                        task_logger.info(f"  - {f}")
                task_logger.info("="*60)
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "iterations": iteration,
                    "duration": duration,
                    "final_output": task.output,
                    "final_status": "completed",
                    "status_block": status_block
                }
            
            elif status_block.status == TaskStatus.NEED_HUMAN:
                task_logger.warning("="*60)
                task_logger.warning("任务需要人类介入")
                task_logger.warning("="*60)
                task_logger.warning(f"原因: {status_block.reason}")
                task_logger.warning(f"介入类型: {status_block.intervention_type}")
                task_logger.warning(f"优先级: {status_block.priority}")
                task_logger.warning(f"迭代次数: {iteration}")
                task_logger.warning("="*60)
                
                return {
                    "success": False,
                    "task_id": task_id,
                    "iterations": iteration,
                    "duration": time.time() - start_time,
                    "final_output": task.output,
                    "final_status": "need_human",
                    "status_block": status_block,
                    "error": f"需要人类介入: {status_block.reason}"
                }
            
            elif status_block.status == TaskStatus.CONTINUE:
                if not self.auto_continue:
                    task_logger.warning("="*60)
                    task_logger.warning("任务需要继续，但自动继续已禁用")
                    task_logger.warning("="*60)
                    task_logger.warning(f"进度: {status_block.progress * 100:.1f}%")
                    task_logger.warning(f"迭代次数: {iteration}")
                    task_logger.warning("="*60)
                    return {
                        "success": False,
                        "task_id": task_id,
                        "iterations": iteration,
                        "duration": time.time() - start_time,
                        "final_output": task.output,
                        "final_status": "continue",
                        "status_block": status_block,
                        "error": "自动继续已禁用"
                    }
                
                task_logger.info("="*60)
                task_logger.info("任务继续执行")
                task_logger.info("="*60)
                task_logger.info(f"进度: {status_block.progress * 100:.1f}%")
                task_logger.info(f"原因: {status_block.reason}")
                task_logger.info(f"下一步: {status_block.next_part}")
                task_logger.info(f"迭代次数: {iteration}")
                task_logger.info("="*60)
                
                # 更新需求，添加继续指令
                requirement = f"继续任务。\n\n上一步: {status_block.reason}\n下一步: {status_block.next_part}"
                continue
            
            elif status_block.status == TaskStatus.ERROR:
                task_logger.error("="*60)
                task_logger.error("任务执行失败")
                task_logger.error("="*60)
                task_logger.error(f"错误信息: {status_block.error_message}")
                task_logger.error(f"迭代次数: {iteration}")
                task_logger.error(f"总耗时: {time.time() - start_time:.2f}秒")
                task_logger.error("="*60)
                
                return {
                    "success": False,
                    "task_id": task_id,
                    "iterations": iteration,
                    "duration": time.time() - start_time,
                    "final_output": task.output,
                    "final_status": "error",
                    "status_block": status_block,
                    "error": status_block.error_message
                }
            
            elif status_block.status == TaskStatus.PARTIAL:
                task_logger.warning("="*60)
                task_logger.warning("任务部分完成")
                task_logger.warning("="*60)
                task_logger.warning(f"置信度: {status_block.confidence}")
                task_logger.warning(f"警告数量: {len(status_block.warnings)}")
                if status_block.warnings:
                    task_logger.warning("警告列表:")
                    for w in status_block.warnings:
                        task_logger.warning(f"  - {w}")
                task_logger.warning(f"迭代次数: {iteration}")
                task_logger.warning("="*60)
                
                # 可以选择继续或停止
                if self.auto_continue and iteration < self.max_iterations:
                    task_logger.info(f"继续处理 {len(status_block.warnings)} 个警告")
                    requirement = f"处理以下警告并完成任务:\n\n{chr(10).join(status_block.warnings)}"
                    continue
                else:
                    return {
                        "success": True,  # 部分完成也算成功
                        "task_id": task_id,
                        "iterations": iteration,
                        "duration": time.time() - start_time,
                        "final_output": task.output,
                        "final_status": "partial",
                        "status_block": status_block
                    }
            
            elif status_block.status == TaskStatus.WAITING:
                task_logger.info("="*60)
                task_logger.info("任务等待中")
                task_logger.info("="*60)
                task_logger.info(f"原因: {status_block.reason}")
                task_logger.info(f"迭代次数: {iteration}")
                task_logger.info("将在2秒后重新检查")
                task_logger.info("="*60)
                time.sleep(2)
                # 不改变requirement，继续下一轮（会重新执行CLI命令）
                continue
        
        # 达到最大迭代次数
        total_duration = time.time() - start_time
        task_logger.warning("="*60)
        task_logger.warning("已达到最大迭代次数")
        task_logger.warning("="*60)
        task_logger.warning(f"最大迭代次数: {self.max_iterations}")
        task_logger.warning(f"总耗时: {total_duration:.2f}秒")
        task_logger.warning(f"平均每轮耗时: {total_duration / iteration:.2f}秒" if iteration > 0 else "平均每轮耗时: N/A")
        task_logger.warning("="*60)
        
        return {
            "success": False,
            "task_id": task_id,
            "iterations": iteration,
            "duration": time.time() - start_time,
            "final_output": all_outputs[-1] if all_outputs else "",
            "final_status": "max_iterations",
            "error": f"达到最大轮数 {self.max_iterations}"
        }
    
    def _execute_single_round(
        self,
        requirement: str,
        project_path: str,
        task_id: str,
        iteration: int
    ) -> ClaudeCodeTask:
        """执行单轮任务"""
        task = ClaudeCodeTask(
            task_id=task_id,
            requirement=requirement,
            project_path=project_path,
            iteration=iteration,
            start_time=time.time()
        )
        
        logger.info("="*60)
        logger.info(f"【第 {iteration} 轮对话】开始执行")
        logger.info("="*60)
        logger.info(f"任务ID: {task_id}")
        logger.info(f"项目路径: {project_path}")
        logger.info(f"需求描述 ({len(requirement)} 字符):")
        logger.info("-"*60)
        logger.info("-"*60)
        
        # 构建命令（使用 /multi-round-protocol，传递 iteration）
        cmd = self._build_command(requirement, project_path, iteration)
        
        # 记录完整命令
        cmd_str = " ".join(cmd)
        logger.info("执行命令:")
        logger.info(f"  CLI路径: {self.cli_path}")
        logger.info(f"  模型: {self.model}")
        logger.info(f"  工作目录: {project_path}")
        logger.info(f"  是否继续会话: {iteration > 1}")
        logger.info(f"  完整命令: {cmd_str}")
        logger.info("-"*60)
        
        # 设置环境变量
        env = os.environ.copy()
        env_info = []
        
        if self.api_key:
            env["ANTHROPIC_API_KEY"] = self.api_key
            env["ANTHROPIC_AUTH_TOKEN"] = self.api_key
            # 只显示前8位和后4位
            masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
            env_info.append(f"ANTHROPIC_API_KEY: {masked_key}")
            env_info.append(f"ANTHROPIC_AUTH_TOKEN: {masked_key}")
        
        if self.api_base_url:
            env["ANTHROPIC_BASE_URL"] = self.api_base_url
            env_info.append(f"ANTHROPIC_BASE_URL: {self.api_base_url}")
        
        if env_info:
            logger.info("环境变量:")
            for info in env_info:
                logger.info(f"  {info}")
        
        try:
            # 执行命令
            logger.info(f"开始执行命令 (超时: {self.timeout}秒)...")
            exec_start = time.time()
            
            if os.name == 'nt':
                # Windows: 使用 PowerShell，指定 UTF-8 编码
                ps_cmd = " ".join(cmd)
                full_ps_cmd = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {ps_cmd}"
                logger.debug(f"PowerShell命令: {full_ps_cmd}")
                
                result = subprocess.run(
                    ["powershell", "-Command", full_ps_cmd],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    cwd=project_path,
                    env=env,
                    timeout=self.timeout
                )
            else:
                # Linux/Mac
                logger.debug(f"Shell命令: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    cwd=project_path,
                    env=env,
                    timeout=self.timeout
                )
            
            exec_duration = time.time() - exec_start
            logger.info(f"命令执行完成，耗时: {exec_duration:.2f}秒")
            
            task.output = result.stdout if result.stdout else ""
            task.end_time = time.time()
            execution_time = task.duration()
            
            # 详细记录输出
            logger.info("="*60)
            logger.info(f"【第 {iteration} 轮对话】执行结果")
            logger.info("="*60)
            logger.info(f"总执行时间: {execution_time:.2f}秒")
            logger.info(f"返回码: {result.returncode}")
            logger.info(f"标准输出长度: {len(task.output)} 字符")
            
            if result.stderr:
                logger.info(f"标准错误长度: {len(result.stderr)} 字符")
            
            logger.info("-"*60)
            logger.info("标准输出 (stdout):")
            logger.info("-"*60)
            if task.output:
                logger.info(task.output)
            else:
                logger.info("(无输出)")
            logger.info("-"*60)
            
            if result.stderr:
                logger.info("标准错误 (stderr):")
                logger.info("-"*60)
                logger.info(result.stderr)
                logger.info("-"*60)
            
            logger.info("="*60)
            
            if result.returncode != 0:
                logger.warning(f"命令返回非零状态码: {result.returncode}", extra={
                    "return_code": result.returncode,
                    "task_id": task_id,
                    "iteration": iteration,
                    "execution_time": execution_time,
                    "has_stderr": bool(result.stderr),
                    "stderr_length": len(result.stderr) if result.stderr else 0
                })
            else:
                logger.info(f"命令执行成功 (返回码: 0)", extra={
                    "task_id": task_id,
                    "iteration": iteration,
                    "execution_time": execution_time,
                    "output_length": len(task.output)
                })
            
            # 保存任务
            self.tasks[task_id] = task
            
            return task
            
        except subprocess.TimeoutExpired as e:
            exec_duration = time.time() - exec_start
            task.output = f"任务超时 ({self.timeout}秒)"
            task.end_time = time.time()
            self.tasks[task_id] = task
            
            logger.error("="*60)
            logger.error(f"【第 {iteration} 轮对话】执行超时")
            logger.error("="*60)
            logger.error(f"超时时间: {self.timeout}秒")
            logger.error(f"实际执行时间: {exec_duration:.2f}秒")
            logger.error(f"任务ID: {task_id}")
            logger.error(f"项目路径: {project_path}")
            logger.error(f"命令: {cmd_str}")
            
            # 尝试获取部分输出
            if hasattr(e, 'stdout') and e.stdout:
                logger.error(f"部分标准输出 ({len(e.stdout)} 字符):")
                logger.error(e.stdout)
            if hasattr(e, 'stderr') and e.stderr:
                logger.error(f"部分标准错误 ({len(e.stderr)} 字符):")
                logger.error(e.stderr)
            
            logger.error("="*60)
            raise RuntimeError(f"任务超时 ({self.timeout}秒)")
        
        except Exception as e:
            exec_duration = time.time() - exec_start if 'exec_start' in locals() else 0
            task.output = f"执行失败: {e}"
            task.end_time = time.time()
            self.tasks[task_id] = task
            
            logger.error("="*60)
            logger.error(f"【第 {iteration} 轮对话】执行失败")
            logger.error("="*60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"执行时间: {exec_duration:.2f}秒")
            logger.error(f"任务ID: {task_id}")
            logger.error(f"项目路径: {project_path}")
            logger.error(f"命令: {cmd_str}")
            logger.error("="*60)
            logger.error("异常堆栈:", exc_info=True)
            
            raise RuntimeError(f"执行任务失败: {e}")
    
    def _build_command(self, requirement: str, project_path: str, iteration: int = 1) -> List[str]:
        """构建 CLI 命令"""
        cmd = [self.cli_path]
        
        # 权限模式（自动批准）
        cmd.extend(["--permission-mode", "bypassPermissions"])
        
        # 非交互式输出
        cmd.append("--print")
        
        # 输出格式：使用 text 格式确保输出到 stdout
        cmd.extend(["--output-format", "text"])
        
        # 第二轮及以后：添加 --continue 继续最近的会话
        if iteration > 1:
            cmd.append("--continue")
        
        # 添加索引目录
        if self.index_directories:
            for idx_dir in self.index_directories:
                cmd.extend(["--add-dir", str(idx_dir)])
        
        # 模型
        #if self.model:
        cmd.extend(["--model", "claude-haiku-4-5-20251001"])
        
        # 第一轮：使用 /multi-round-protocol 加载 skill
        # 第二轮及以后：直接发送 requirement（skill 已加载）

        prompt = f'"/multi-round-protocol {requirement}"'

        
        cmd.append(prompt)
        
        # 记录命令构建详情
        logger.debug("命令构建详情:", extra={
            "cli_path": self.cli_path,
            "permission_mode": "bypassPermissions",
            "output_format": "text",
            "use_continue": iteration > 1,
            "model": self.model,
            "index_dirs_count": len(self.index_directories) if self.index_directories else 0,
            "index_dirs": self.index_directories if self.index_directories else [],
            "prompt_length": len(requirement),
            "use_multi_round_protocol": iteration == 1,
            "full_command": " ".join(cmd)
        })
        
        return cmd
    
    def _parse_status_block(self, output: str) -> Optional[StatusBlock]:
        """解析状态块"""
        # 查找状态块
        pattern = r'---TASK_STATUS---(.*?)---END_STATUS---'
        match = re.search(pattern, output, re.DOTALL)
        
        if not match:
            logger.debug("输出中未找到状态块", extra={
                "output_length": len(output),
                "output_preview": output[:200] if output else "(空输出)"
            })
            return None
        
        status_text = match.group(1).strip()
        logger.info("="*60)
        logger.info("解析状态块")
        logger.info("="*60)
        logger.info(f"状态块内容 ({len(status_text)} 字符):")
        logger.info("-"*60)
        logger.info(status_text)
        logger.info("-"*60)
        
        try:
            # 解析 YAML
            data = yaml.safe_load(status_text)
            
            logger.info("YAML 解析成功:")
            for key, value in data.items():
                if isinstance(value, list):
                    logger.info(f"  {key}: [{len(value)} 项]")
                    for item in value:
                        logger.info(f"    - {item}")
                else:
                    logger.info(f"  {key}: {value}")
            
            # 解析状态
            status_str = data.get('status', 'unknown')
            try:
                status = TaskStatus(status_str)
                logger.info(f"状态: {status.value}")
            except ValueError:
                status = TaskStatus.UNKNOWN
                logger.warning(f"未知状态值: {status_str}，使用 UNKNOWN")
            
            # 构建状态块
            status_block = StatusBlock(
                status=status,
                reason=data.get('reason', ''),
                confidence=float(data.get('confidence', 0.0)),
                progress=float(data.get('progress', 0.0)),
                next_part=data.get('next_part', ''),
                error_message=data.get('error_message', ''),
                intervention_type=data.get('intervention_type', ''),
                priority=data.get('priority', ''),
                files_modified=data.get('files_modified', []),
                warnings=data.get('warnings', [])
            )
            
            logger.info("="*60)
            return status_block
            
        except yaml.YAMLError as e:
            logger.error("="*60)
            logger.error("YAML 解析失败")
            logger.error("="*60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"状态块内容 ({len(status_text)} 字符):")
            logger.error(status_text)
            logger.error("="*60)
            return None
        except Exception as e:
            logger.error("="*60)
            logger.error("状态块解析失败")
            logger.error("="*60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error("="*60)
            logger.error("异常堆栈:", exc_info=True)
            return None
    
    def analyze_error(
        self,
        error_log: str,
        code_context: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """分析错误日志"""
        prompt = f"分析以下错误并提供修复建议：\n\n{error_log}"
        
        if code_context:
            prompt += f"\n\n相关代码：\n{code_context}"
        
        return self.generate_code(prompt, **kwargs)
    
    def generate_fix(
        self,
        error_analysis: str,
        original_code: str,
        **kwargs
    ) -> AIResponse:
        """生成修复代码"""
        prompt = f"""
根据错误分析修复代码：

错误分析：
{error_analysis}

原始代码：
{original_code}

请提供修复后的代码。
"""
        return self.generate_code(prompt, **kwargs)
    
    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """生成响应（通用方法）"""
        requirement = "\n".join([msg.content for msg in messages])
        
        if system_prompt:
            requirement = f"{system_prompt}\n\n{requirement}"
        
        return self.generate_code(requirement, **kwargs)
    
    def get_task_info(self, task_id: str) -> Optional[ClaudeCodeTask]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        return [
            {
                "task_id": task.task_id,
                "iteration": task.iteration,
                "status": task.status_block.status.value if task.status_block else "unknown",
                "duration": task.duration()
            }
            for task in self.tasks.values()
        ]
