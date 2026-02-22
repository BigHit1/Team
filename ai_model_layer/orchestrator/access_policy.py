"""
权限策略
基于 Agent 配置和工作区结构的权限管理
"""

from pathlib import Path
from typing import List, Set, Optional, Dict, Any
from enum import Enum

from .workspace import Workspace, WorkspaceZone


class Permission(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class AccessPolicy:
    """
    访问策略
    根据 Agent 的权限配置和工作区结构，判断是否允许访问
    """
    
    def __init__(self, workspace: Workspace):
        """
        初始化访问策略
        
        Args:
            workspace: 工作区实例
        """
        self.workspace = workspace
    
    def check_access(
        self,
        agent_config: Dict[str, Any],
        file_path: Path,
        permission: Permission,
        phase_name: Optional[str] = None,
        iteration: int = 1
    ) -> bool:
        """
        检查 Agent 是否有权限访问指定文件
        
        Args:
            agent_config: Agent 配置（包含权限声明）
            file_path: 文件路径
            permission: 权限类型
            phase_name: 阶段名称（用于临时目录隔离）
            iteration: 迭代次数
        
        Returns:
            是否允许访问
        """
        file_path = Path(file_path).resolve()
        
        # 读取权限：默认所有 Agent 都可以读取
        if permission == Permission.READ:
            read_zones = agent_config.get("read_zones", ["*"])
            if "*" in read_zones or "all" in read_zones:
                return True
            
            # 检查是否在允许的区域内
            for zone_name in read_zones:
                try:
                    zone = WorkspaceZone(zone_name)
                    if self.workspace.is_in_zone(file_path, zone):
                        return True
                except ValueError:
                    continue
            
            return False
        
        # 写入权限：根据 Agent 配置的 write_zones
        if permission == Permission.WRITE:
            write_zones = agent_config.get("write_zones", [])
            
            # 检查是否在允许的区域内
            for zone_config in write_zones:
                if isinstance(zone_config, str):
                    # 简单字符串：直接匹配区域
                    zone_name = zone_config
                    subdir = None
                elif isinstance(zone_config, dict):
                    # 字典配置：可以指定子目录
                    zone_name = zone_config.get("zone")
                    subdir = zone_config.get("subdir")
                else:
                    continue
                
                try:
                    zone = WorkspaceZone(zone_name)
                    zone_path = self.workspace.get_zone_path(zone)
                    
                    # 如果指定了子目录
                    if subdir:
                        if zone == WorkspaceZone.DOCS:
                            zone_path = self.workspace.get_doc_subdir(subdir)
                        elif zone == WorkspaceZone.TEMP:
                            # 临时目录使用阶段和迭代隔离
                            if phase_name:
                                zone_path = self.workspace.get_temp_subdir(phase_name, iteration)
                            else:
                                zone_path = zone_path / subdir
                        else:
                            zone_path = zone_path / subdir
                    
                    # 检查文件是否在允许的路径下
                    zone_path = zone_path.resolve()
                    try:
                        file_path.relative_to(zone_path)
                        return True
                    except ValueError:
                        continue
                        
                except ValueError:
                    continue
            
            # 特殊处理：project 区域需要排除工作区目录
            if "project" in [z if isinstance(z, str) else z.get("zone") for z in write_zones]:
                # 检查是否在项目根目录下
                try:
                    file_path.relative_to(self.workspace.project_path)
                    # 但不能在工作区目录下
                    if not self.workspace.is_in_workspace(file_path):
                        return True
                except ValueError:
                    pass
            
            return False
        
        # 删除权限：通常与写入权限相同
        if permission == Permission.DELETE:
            return self.check_access(agent_config, file_path, Permission.WRITE, phase_name, iteration)
        
        return False
    
    def get_writable_paths(
        self,
        agent_config: Dict[str, Any],
        phase_name: Optional[str] = None,
        iteration: int = 1
    ) -> List[Path]:
        """
        获取 Agent 可写入的路径列表
        
        Args:
            agent_config: Agent 配置
            phase_name: 阶段名称
            iteration: 迭代次数
        
        Returns:
            可写入的路径列表
        """
        writable_paths = []
        write_zones = agent_config.get("write_zones", [])
        
        for zone_config in write_zones:
            if isinstance(zone_config, str):
                zone_name = zone_config
                subdir = None
            elif isinstance(zone_config, dict):
                zone_name = zone_config.get("zone")
                subdir = zone_config.get("subdir")
            else:
                continue
            
            try:
                zone = WorkspaceZone(zone_name)
                zone_path = self.workspace.get_zone_path(zone)
                
                if subdir:
                    if zone == WorkspaceZone.DOCS:
                        zone_path = self.workspace.get_doc_subdir(subdir)
                    elif zone == WorkspaceZone.TEMP:
                        if phase_name:
                            zone_path = self.workspace.get_temp_subdir(phase_name, iteration)
                        else:
                            zone_path = zone_path / subdir
                    else:
                        zone_path = zone_path / subdir
                
                writable_paths.append(zone_path)
                
            except ValueError:
                continue
        
        return writable_paths
    
    def get_guidance(self, agent_config: Dict[str, Any]) -> str:
        """
        生成 Agent 的文件操作指导
        
        Args:
            agent_config: Agent 配置
        
        Returns:
            文件操作指导文本
        """
        agent_name = agent_config.get("name", "Agent")
        read_zones = agent_config.get("read_zones", ["*"])
        write_zones = agent_config.get("write_zones", [])
        
        # 工作区结构信息
        structure_info = self.workspace.get_structure_info()
        
        # 读取权限
        if "*" in read_zones or "all" in read_zones:
            read_info = "- ✅ 读取任何项目文件"
        else:
            read_info = "- ✅ 读取以下区域的文件:\n"
            for zone in read_zones:
                read_info += f"  - {zone}\n"
        
        # 写入权限
        write_info = ""
        if write_zones:
            write_info = "- ✅ 写入以下区域:\n"
            for zone_config in write_zones:
                if isinstance(zone_config, str):
                    write_info += f"  - {zone_config}/\n"
                elif isinstance(zone_config, dict):
                    zone_name = zone_config.get("zone")
                    subdir = zone_config.get("subdir")
                    if subdir:
                        write_info += f"  - {zone_name}/{subdir}/\n"
                    else:
                        write_info += f"  - {zone_name}/\n"
        else:
            write_info = "- ❌ 无写入权限（只读 Agent）"
        
        # 限制说明
        restrictions = agent_config.get("restrictions", [])
        restrictions_info = ""
        if restrictions:
            restrictions_info = "\n你不可以:\n"
            for restriction in restrictions:
                restrictions_info += f"- ❌ {restriction}\n"
        
        return f"""
{structure_info}

## 你的权限

{read_info}

{write_info}
{restrictions_info}

**提示**: {agent_config.get('guidance', '请根据你的职责合理使用文件系统。')}
"""

