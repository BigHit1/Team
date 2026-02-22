"""
文件访问策略
定义不同 Agent 可以访问的文件路径和操作权限
"""

from pathlib import Path
from typing import List, Set, Optional
from enum import Enum


class FileOperation(Enum):
    """文件操作类型"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class FilePolicy:
    """文件访问策略"""
    
    def __init__(self, project_path: str, run_id: Optional[str] = None):
        self.project_path = Path(project_path)
        self.run_id = run_id
        
        # 定义不同的工作区域
        self.workspace_root = self.project_path / ".claude"
        
        # 如果有 run_id，使用隔离的目录结构
        if run_id:
            self.run_root = self.workspace_root / "runs" / run_id
            self.phases_dir = self.run_root / "phases"
            self.docs_dir = self.run_root / "docs"
            self.temp_dir = self.run_root / "temp"
            self.diagrams_dir = self.run_root / "diagrams"
        else:
            # 回退到旧的目录结构（兼容性）
            self.phases_dir = self.workspace_root / "phases"
            self.docs_dir = self.workspace_root / "docs"
            self.temp_dir = self.workspace_root / "temp"
            self.diagrams_dir = self.workspace_root / "diagrams"
        
    def get_allowed_write_paths(self, agent_role: str, phase_name: str = None, iteration: int = 1) -> List[Path]:
        """
        获取 Agent 允许写入的路径
        
        Args:
            agent_role: Agent 角色（planner, architect, coder, reviewer）
            phase_name: 阶段名称
            iteration: 迭代次数
        
        Returns:
            允许写入的路径列表
        """
        allowed_paths = []
        
        # 所有 Agent 都可以写入临时目录
        if phase_name and iteration:
            # 为每个阶段和迭代创建独立的临时目录
            temp_phase_dir = self.temp_dir / phase_name / f"iter_{iteration}"
            allowed_paths.append(temp_phase_dir)
        else:
            allowed_paths.append(self.temp_dir)
        
        # 根据角色分配不同的写入权限
        if agent_role == "planner":
            # 规划者：可以写入文档目录
            allowed_paths.extend([
                self.docs_dir / "plans",
                self.temp_dir / "planning"
            ])
            
        elif agent_role == "architect":
            # 架构师：可以写入架构文档和图表
            allowed_paths.extend([
                self.docs_dir / "architecture",
                self.diagrams_dir,
                self.temp_dir / "architecture"
            ])
            
        elif agent_role == "coder" or agent_role == "ue5-code-guide":
            # 编码者：可以写入项目代码（但不包括 .claude 目录）
            allowed_paths.append(self.project_path)
            
        elif agent_role == "reviewer":
            # 审查者：可以写入审查报告
            allowed_paths.extend([
                self.docs_dir / "reviews",
                self.temp_dir / "reviews"
            ])
        
        return allowed_paths
    
    def is_path_allowed(
        self,
        agent_role: str,
        file_path: str,
        operation: FileOperation,
        phase_name: str = None,
        iteration: int = 1
    ) -> bool:
        """
        检查 Agent 是否允许对指定路径执行操作
        
        Args:
            agent_role: Agent 角色
            file_path: 文件路径
            operation: 操作类型
            phase_name: 阶段名称
            iteration: 迭代次数
        
        Returns:
            是否允许
        """
        file_path = Path(file_path).resolve()
        
        # 读取操作：所有 Agent 都可以读取项目文件
        if operation == FileOperation.READ:
            return True
        
        # 写入和删除操作：检查路径是否在允许列表中
        if operation in [FileOperation.WRITE, FileOperation.DELETE]:
            allowed_paths = self.get_allowed_write_paths(agent_role, phase_name, iteration)
            
            for allowed_path in allowed_paths:
                allowed_path = allowed_path.resolve()
                try:
                    # 检查文件是否在允许的路径下
                    file_path.relative_to(allowed_path)
                    return True
                except ValueError:
                    continue
            
            # 特殊规则：coder 可以写入项目根目录（但不能写入 .claude 目录）
            if agent_role in ["coder", "ue5-code-guide"]:
                try:
                    # 检查是否在项目根目录下
                    file_path.relative_to(self.project_path)
                    # 但不能在 .claude 目录下
                    try:
                        file_path.relative_to(self.workspace_root)
                        return False  # 在 .claude 目录下，不允许
                    except ValueError:
                        return True  # 不在 .claude 目录下，允许
                except ValueError:
                    pass
            
            return False
        
        return False
    
    def get_phase_output_path(self, phase_name: str, iteration: int = 1) -> Path:
        """
        获取阶段输出文件路径（支持多次迭代）
        
        Args:
            phase_name: 阶段名称
            iteration: 迭代次数（默认为1）
        
        Returns:
            输出文件路径
        """
        if iteration == 1:
            # 第一次执行：使用标准路径
            return self.phases_dir / f"{phase_name}.md"
        else:
            # 后续执行：添加迭代编号
            return self.phases_dir / f"{phase_name}_iter{iteration}.md"
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        dirs = [
            self.workspace_root,
            self.phases_dir,
            self.docs_dir,
            self.temp_dir,
            self.diagrams_dir,
            self.docs_dir / "plans",
            self.docs_dir / "architecture",
            self.docs_dir / "reviews",
            self.temp_dir / "planning",
            self.temp_dir / "architecture",
            self.temp_dir / "reviews"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_guidance(self, agent_name: str) -> str:
        """
        获取 Agent 的文件操作指导
        
        Args:
            agent_name: Agent 名称
        
        Returns:
            文件操作指导文本
        """
        # 根据是否有 run_id 生成不同的路径
        if self.run_id:
            base_path = f".claude/runs/{self.run_id}"
        else:
            base_path = ".claude/runs/default"
        
        # 为不同 Agent 生成指导
        if agent_name == "planner":
            return f"""
你可以：
- ✅ 创建详细文档（.md, .txt）到 {base_path}/docs/plans/
- ✅ 创建临时文件到 {base_path}/temp/planning/
- ✅ 读取任何项目文件

你不可以：
- ❌ 创建或修改代码文件（.cpp, .h, .py 等）
- ❌ 修改项目源代码

**重要**：你的主要输出应该在回复中，详细的补充文档可以创建到上述目录。
"""
        
        elif agent_name == "architect":
            return f"""
你可以：
- ✅ 创建详细架构文档（.md, .txt）到 {base_path}/docs/architecture/
- ✅ 创建架构图（.puml, .mermaid, .svg）到 {base_path}/diagrams/
- ✅ 创建临时文件到 {base_path}/temp/architecture/
- ✅ 读取任何项目文件

你不可以：
- ❌ 创建或修改代码文件（.cpp, .h, .py 等）
- ❌ 修改项目源代码

**重要**：你的主要输出应该在回复中，详细的补充文档可以创建到上述目录。
"""
        
        elif agent_name == "ue5-code-guide":
            return """
你可以：
- ✅ 创建和修改项目代码文件
- ✅ 创建和修改 UE5 配置文件
- ✅ 读取任何项目文件

你不可以：
- ❌ 修改 .claude/ 目录下的文件
"""
        
        elif agent_name == "code-reviewer":
            return f"""
你可以：
- ✅ 创建详细审查报告（.md, .txt）到 {base_path}/docs/reviews/
- ✅ 创建临时文件到 {base_path}/temp/reviews/
- ✅ 读取任何项目文件

你不可以：
- ❌ 创建或修改代码文件
- ❌ 修改项目源代码

**重要**：你的主要输出应该在回复中，详细的补充文档可以创建到上述目录。
"""
        
        return ""


