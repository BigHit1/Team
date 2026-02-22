"""
Agent 库管理
负责加载和管理所有 Agent 定义
"""

from pathlib import Path
from typing import Dict, Optional
import re
from ..utils.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


class AgentLibrary:
    """Agent 库"""
    
    def __init__(self, agents_dir: Optional[Path] = None):
        """
        初始化 Agent 库
        
        Args:
            agents_dir: Agent 目录，默认为 ai_model_layer/agents/standard_agents
        """
        if agents_dir is None:
            # 默认使用标准 Agent 库
            agents_dir = Path(__file__).parent / "standard_agents"
        
        self.agents_dir = Path(agents_dir)
        self.agents: Dict[str, Dict] = {}
        
        # 加载所有 Agents
        self._load_agents()
    
    def _load_agents(self):
        """加载所有 Agent 定义"""
        if not self.agents_dir.exists():
            logger.warning(f"Agent 目录不存在: {self.agents_dir}")
            return
        
        logger.info(f"从目录加载 Agents: {self.agents_dir}")
        
        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            agent_data = self._parse_agent_file(agent_file)
            
            if agent_data:
                self.agents[agent_name] = agent_data
                logger.info(f"加载 Agent: {agent_name}")
        
        logger.info(f"共加载 {len(self.agents)} 个 Agents")
    
    def _parse_agent_file(self, file_path: Path) -> Optional[Dict]:
        """
        解析 Agent 文件
        
        格式：
        ---
        name: planner
        description: 规划专家
        model: opus
        tools: ["Read", "Grep", "Glob"]
        read_zones: ["*"]
        write_zones:
          - zone: "docs"
            subdir: "plans"
        restrictions: ["创建代码文件"]
        guidance: "提示信息"
        ---
        
        # Agent 内容
        ...
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 解析 YAML 前置元数据
            metadata = {}
            prompt = content
            
            # 检查是否有 YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # 使用 YAML 解析器
                    import yaml
                    try:
                        metadata = yaml.safe_load(parts[1].strip()) or {}
                    except yaml.YAMLError:
                        # 回退到简单解析
                        frontmatter = parts[1].strip()
                        for line in frontmatter.split('\n'):
                            if ':' in line and not line.strip().startswith('-'):
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # 简单解析
                                if value.startswith('[') and value.endswith(']'):
                                    # 列表
                                    value = [v.strip().strip('"').strip("'") 
                                            for v in value[1:-1].split(',') if v.strip()]
                                
                                metadata[key] = value
                    
                    # 提示内容
                    prompt = parts[2].strip()
            
            return {
                "name": metadata.get("name", file_path.stem),
                "description": metadata.get("description", ""),
                "model": metadata.get("model", "sonnet"),
                "tools": metadata.get("tools", []),
                "read_zones": metadata.get("read_zones", ["*"]),
                "write_zones": metadata.get("write_zones", []),
                "restrictions": metadata.get("restrictions", []),
                "guidance": metadata.get("guidance", ""),
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"解析 Agent 文件失败 {file_path}: {e}", exc_info=True)
            return None
    
    def get_agent(self, agent_name: str) -> Optional[Dict]:
        """获取 Agent 定义"""
        return self.agents.get(agent_name)
    
    def get_agent_prompt(self, agent_name: str) -> str:
        """获取 Agent 提示词"""
        agent = self.get_agent(agent_name)
        if agent:
            return agent["prompt"]
        return ""
    
    def list_agents(self) -> Dict[str, str]:
        """列出所有 Agents"""
        return {
            name: agent["description"]
            for name, agent in self.agents.items()
        }
    
    def reload(self):
        """重新加载所有 Agents"""
        logger.info("重新加载所有 Agents")
        self.agents.clear()
        self._load_agents()

