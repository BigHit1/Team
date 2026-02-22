"""
Git 包装器
自动检测和使用内嵌的 Git
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List
from .logger import get_logger

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取日志器
logger = get_logger(__name__)


class GitWrapper:
    """Git 包装器 - 自动使用内嵌 Git"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        初始化 Git 包装器
        
        Args:
            project_root: 项目根目录，默认自动检测
        """
        if project_root is None:
            # 自动检测项目根目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
        
        self.project_root = Path(project_root)
        self.git_path = self._find_git()
        self.bash_path = self._find_bash()
    
    def _find_git(self) -> Optional[Path]:
        """
        查找 Git 可执行文件
        
        优先级：
        1. 内嵌 Git (tools/git/bin/git.exe)
        2. 环境变量 GIT_PATH
        3. 系统 PATH
        """
        # 1. 内嵌 Git
        embedded_git = self.project_root / "tools" / "git" / "bin" / "git.exe"
        if embedded_git.exists():
            logger.info(f"使用内嵌 Git: {embedded_git}")
            return embedded_git
        
        # 2. 环境变量
        env_git = os.getenv("GIT_PATH")
        if env_git and Path(env_git).exists():
            logger.info(f"使用环境变量 Git: {env_git}")
            return Path(env_git)
        
        # 3. 系统 PATH
        try:
            result = subprocess.run(
                ["where", "git"] if os.name == "nt" else ["which", "git"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_path = result.stdout.strip().split('\n')[0]
                logger.info(f"使用系统 Git: {git_path}")
                return Path(git_path)
        except Exception as e:
            logger.warning(f"查找系统 Git 失败: {e}")
        
        logger.error("未找到 Git")
        return None
    
    def _find_bash(self) -> Optional[Path]:
        """
        查找 bash.exe
        
        优先级：
        1. 内嵌 Git bash (tools/git/bin/bash.exe)
        2. 环境变量 CLAUDE_CODE_GIT_BASH_PATH
        3. Git 安装目录下的 bash.exe
        """
        # 1. 内嵌 Git bash
        embedded_bash = self.project_root / "tools" / "git" / "bin" / "bash.exe"
        if embedded_bash.exists():
            logger.info(f"使用内嵌 bash: {embedded_bash}")
            return embedded_bash
        
        # 2. 环境变量
        env_bash = os.getenv("CLAUDE_CODE_GIT_BASH_PATH")
        if env_bash and Path(env_bash).exists():
            logger.info(f"使用环境变量 bash: {env_bash}")
            return Path(env_bash)
        
        # 3. Git 安装目录
        if self.git_path:
            # 尝试 bin/bash.exe
            bash_path = self.git_path.parent / "bash.exe"
            if bash_path.exists():
                logger.info(f"使用 Git 目录 bash: {bash_path}")
                return bash_path
            
            # 尝试 usr/bin/bash.exe
            bash_path = self.git_path.parent.parent / "usr" / "bin" / "bash.exe"
            if bash_path.exists():
                logger.info(f"使用 Git usr/bin bash: {bash_path}")
                return bash_path
        
        logger.error("未找到 bash.exe")
        return None
    
    def is_available(self) -> bool:
        """检查 Git 是否可用"""
        return self.git_path is not None and self.git_path.exists()
    
    def is_bash_available(self) -> bool:
        """检查 bash 是否可用"""
        return self.bash_path is not None and self.bash_path.exists()
    
    def run(
        self,
        args: List[str],
        cwd: Optional[str] = None,
        capture_output: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        运行 Git 命令
        
        Args:
            args: Git 命令参数（不包含 'git'）
            cwd: 工作目录
            capture_output: 是否捕获输出
            **kwargs: 其他 subprocess 参数
        
        Returns:
            subprocess.CompletedProcess
        """
        if not self.is_available():
            raise RuntimeError("Git 不可用，请运行 setup_git.py 安装")
        
        cmd = [str(self.git_path)] + args
        
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            **kwargs
        )
    
    def get_bash_path(self) -> str:
        """获取 bash.exe 路径（用于 Claude Code CLI）"""
        if not self.is_bash_available():
            raise RuntimeError("bash.exe 不可用，请运行 setup_git.py 安装")
        
        return str(self.bash_path)
    
    def get_git_path(self) -> str:
        """获取 git.exe 路径"""
        if not self.is_available():
            raise RuntimeError("Git 不可用，请运行 setup_git.py 安装")
        
        return str(self.git_path)
    
    def version(self) -> str:
        """获取 Git 版本"""
        if not self.is_available():
            return "未安装"
        
        try:
            result = self.run(["--version"])
            return result.stdout.strip()
        except Exception as e:
            return f"获取版本失败: {e}"
    
    def status(self, repo_path: Optional[str] = None) -> str:
        """获取 Git 状态"""
        result = self.run(["status", "--porcelain"], cwd=repo_path)
        return result.stdout
    
    def has_changes(self, repo_path: Optional[str] = None) -> bool:
        """检查是否有未提交的变更"""
        status = self.status(repo_path)
        return bool(status.strip())
    
    def get_changed_files(self, repo_path: Optional[str] = None) -> List[str]:
        """获取变更的文件列表"""
        status = self.status(repo_path)
        files = []
        
        for line in status.split('\n'):
            if line.strip():
                # 格式: "XY filename"
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    files.append(parts[1])
        
        return files


# 全局实例
_git_wrapper: Optional[GitWrapper] = None


def get_git_wrapper(project_root: Optional[str] = None) -> GitWrapper:
    """
    获取全局 Git 包装器实例
    
    Args:
        project_root: 项目根目录
    
    Returns:
        GitWrapper 实例
    """
    global _git_wrapper
    
    if _git_wrapper is None:
        _git_wrapper = GitWrapper(project_root)
    
    return _git_wrapper


if __name__ == "__main__":
    # 测试
    from .logger import setup_logging
    
    setup_logging(
        log_dir="logs",
        console_level="INFO",
        file_level="DEBUG"
    )
    
    logger.info("="*60)
    logger.info("Git 包装器测试")
    logger.info("="*60)
    
    git = GitWrapper()
    
    logger.info(f"Git 可用: {git.is_available()}")
    logger.info(f"Bash 可用: {git.is_bash_available()}")
    
    if git.is_available():
        logger.info(f"Git 路径: {git.get_git_path()}")
        logger.info(f"Git 版本: {git.version()}")
    
    if git.is_bash_available():
        logger.info(f"Bash 路径: {git.get_bash_path()}")
    
    logger.info("="*60)

