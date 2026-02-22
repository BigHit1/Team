"""
工作区管理
定义 AI 工程的标准目录结构和区域划分
"""

from pathlib import Path
from typing import Dict, Optional
from enum import Enum


class WorkspaceZone(Enum):
    """工作区区域类型"""
    OUTPUT = "output"           # 输出区：最终产物
    TEMP = "temp"              # 临时区：过程文件
    DOCS = "docs"              # 文档区：文档和报告
    DIAGRAMS = "diagrams"      # 图表区：架构图、流程图
    PHASES = "phases"          # 阶段区：各阶段的输出
    PROJECT = "project"        # 项目区：项目源代码


class Workspace:
    """
    工作区管理器
    负责定义和管理 AI 工程的目录结构
    """
    
    def __init__(self, project_path: str, run_id: Optional[str] = None):
        """
        初始化工作区
        
        Args:
            project_path: 项目根路径
            run_id: 运行ID（可选，用于隔离不同运行）
        """
        self.project_path = Path(project_path).resolve()
        self.run_id = run_id
        
        # 工作区根目录
        self.workspace_root = self.project_path / ".claude"
        
        # 如果有 run_id，使用隔离的运行目录
        if run_id:
            self.run_root = self.workspace_root / "runs" / run_id
        else:
            # 使用默认运行目录
            self.run_root = self.workspace_root / "runs" / "default"
        
        # 定义各个区域的路径
        self._zones: Dict[WorkspaceZone, Path] = {
            WorkspaceZone.OUTPUT: self.run_root / "output",
            WorkspaceZone.TEMP: self.run_root / "temp",
            WorkspaceZone.DOCS: self.run_root / "docs",
            WorkspaceZone.DIAGRAMS: self.run_root / "diagrams",
            WorkspaceZone.PHASES: self.run_root / "phases",
            WorkspaceZone.PROJECT: self.project_path
        }
        
        # 文档区的子目录
        self._doc_subdirs = {
            "plans": self._zones[WorkspaceZone.DOCS] / "plans",
            "architecture": self._zones[WorkspaceZone.DOCS] / "architecture",
            "reviews": self._zones[WorkspaceZone.DOCS] / "reviews",
            "reports": self._zones[WorkspaceZone.DOCS] / "reports"
        }
    
    def get_zone_path(self, zone: WorkspaceZone) -> Path:
        """
        获取指定区域的路径
        
        Args:
            zone: 区域类型
        
        Returns:
            区域路径
        """
        return self._zones[zone]
    
    def get_doc_subdir(self, subdir_name: str) -> Path:
        """
        获取文档子目录路径
        
        Args:
            subdir_name: 子目录名称（plans/architecture/reviews/reports）
        
        Returns:
            子目录路径
        """
        return self._doc_subdirs.get(subdir_name, self._zones[WorkspaceZone.DOCS] / subdir_name)
    
    def get_temp_subdir(self, phase_name: str, iteration: int = 1) -> Path:
        """
        获取临时子目录（按阶段和迭代隔离）
        
        Args:
            phase_name: 阶段名称
            iteration: 迭代次数
        
        Returns:
            临时子目录路径
        """
        return self._zones[WorkspaceZone.TEMP] / phase_name / f"iter_{iteration}"
    
    def get_phase_output_path(self, phase_name: str, output_file: str, iteration: int = 1) -> Path:
        """
        获取阶段输出文件路径
        
        Args:
            phase_name: 阶段名称
            output_file: 输出文件名
            iteration: 迭代次数
        
        Returns:
            输出文件路径
        """
        if iteration == 1:
            return self._zones[WorkspaceZone.PHASES] / output_file
        else:
            # 添加迭代编号
            file_stem = Path(output_file).stem
            file_suffix = Path(output_file).suffix
            return self._zones[WorkspaceZone.PHASES] / f"{file_stem}_iter{iteration}{file_suffix}"
    
    def is_in_zone(self, file_path: Path, zone: WorkspaceZone) -> bool:
        """
        检查文件是否在指定区域内
        
        Args:
            file_path: 文件路径
            zone: 区域类型
        
        Returns:
            是否在区域内
        """
        file_path = Path(file_path).resolve()
        zone_path = self._zones[zone].resolve()
        
        try:
            file_path.relative_to(zone_path)
            return True
        except ValueError:
            return False
    
    def is_in_workspace(self, file_path: Path) -> bool:
        """
        检查文件是否在工作区内（.claude 目录）
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否在工作区内
        """
        file_path = Path(file_path).resolve()
        workspace_root = self.workspace_root.resolve()
        
        try:
            file_path.relative_to(workspace_root)
            return True
        except ValueError:
            return False
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        # 创建所有区域目录
        for zone_path in self._zones.values():
            zone_path.mkdir(parents=True, exist_ok=True)
        
        # 创建文档子目录
        for subdir_path in self._doc_subdirs.values():
            subdir_path.mkdir(parents=True, exist_ok=True)
    
    def get_structure_info(self) -> str:
        """
        获取工作区结构信息（用于告知 Agent）
        
        Returns:
            工作区结构描述
        """
        relative_run_root = self.run_root.relative_to(self.project_path)
        
        return f"""
## 工作区结构

项目根目录: {self.project_path.name}/
工作区根目录: {relative_run_root}/

### 区域划分

1. **输出区** (output/)
   - 用途: 存放最终产物和交付物
   - 路径: {relative_run_root}/output/

2. **临时区** (temp/)
   - 用途: 存放过程文件和临时数据
   - 路径: {relative_run_root}/temp/
   - 结构: temp/{{phase_name}}/iter_{{iteration}}/

3. **文档区** (docs/)
   - 用途: 存放文档和报告
   - 路径: {relative_run_root}/docs/
   - 子目录:
     - docs/plans/ - 规划文档
     - docs/architecture/ - 架构文档
     - docs/reviews/ - 审查报告
     - docs/reports/ - 其他报告

4. **图表区** (diagrams/)
   - 用途: 存放架构图、流程图等
   - 路径: {relative_run_root}/diagrams/

5. **阶段区** (phases/)
   - 用途: 存放各阶段的主要输出
   - 路径: {relative_run_root}/phases/

6. **项目区** (项目源代码)
   - 用途: 项目的源代码和配置文件
   - 路径: {self.project_path.name}/
"""
    
    def __repr__(self) -> str:
        return f"<Workspace project={self.project_path.name} run_id={self.run_id}>"

