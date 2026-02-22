"""
配置管理模块
负责加载和管理所有配置文件
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为项目根目录的 config/
        """
        # 确定配置目录
        if config_dir is None:
            # 获取项目根目录
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = project_root / "config"
        else:
            config_dir = Path(config_dir)
        
        self.config_dir = config_dir
        
        # 加载配置文件
        self.ai_config = self._load_yaml("ai_config.yaml")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def get_ai_client_config(self, client_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取 AI 客户端配置
        
        Args:
            client_type: 客户端类型，如果为 None 则使用默认类型
        
        Returns:
            客户端配置字典
        """
        if client_type is None:
            client_type = self.ai_config["ai_client"]["default"]
        
        return self.ai_config["ai_client"].get(client_type, {})
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取 Agent 配置"""
        return self.ai_config["agents"].get(agent_name, {})
    
    def get_prompt(self, prompt_name: str) -> str:
        """获取 Prompt 模板"""
        return self.ai_config.get("prompts", {}).get(prompt_name, "")
    
    def __repr__(self) -> str:
        return f"<Config config_dir={self.config_dir}>"


# 全局配置实例（单例）
_global_config: Optional[Config] = None


def get_config(config_dir: Optional[str] = None) -> Config:
    """
    获取全局配置实例
    
    Args:
        config_dir: 配置文件目录
    
    Returns:
        Config 实例
    """
    global _global_config
    
    if _global_config is None:
        _global_config = Config(config_dir)
    
    return _global_config
