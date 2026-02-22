"""
AI 客户端基类
定义统一的 AI 调用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AIMessage:
    """AI 消息"""
    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """AI 响应"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str  # stop, length, error
    metadata: Optional[Dict[str, Any]] = None


class AIClient(ABC):
    """AI 客户端抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 AI 客户端
        
        Args:
            config: 客户端配置
        """
        self.config = config
        self.model = config.get("model", "")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.7)
        self.timeout = config.get("timeout", 300)
    
    @abstractmethod
    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        生成 AI 响应
        
        Args:
            messages: 消息列表
            system_prompt: 系统提示词
            **kwargs: 其他参数
        
        Returns:
            AI 响应
        """
        pass
    
    @abstractmethod
    def generate_code(
        self,
        requirement: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIResponse:
        """
        生成代码
        
        Args:
            requirement: 需求描述
            context: 上下文信息（项目结构、现有代码等）
            **kwargs: 其他参数
        
        Returns:
            AI 响应（包含生成的代码）
        """
        pass
    
    @abstractmethod
    def analyze_error(
        self,
        error_log: str,
        code_context: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        分析错误日志
        
        Args:
            error_log: 错误日志
            code_context: 相关代码上下文
            **kwargs: 其他参数
        
        Returns:
            AI 响应（包含错误分析）
        """
        pass
    
    @abstractmethod
    def generate_fix(
        self,
        error_analysis: str,
        original_code: str,
        **kwargs
    ) -> AIResponse:
        """
        生成修复代码
        
        Args:
            error_analysis: 错误分析结果
            original_code: 原始代码
            **kwargs: 其他参数
        
        Returns:
            AI 响应（包含修复代码）
        """
        pass
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        required_fields = ["model", "max_tokens"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"配置缺少必需字段: {field}")
        return True
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.model}>"

