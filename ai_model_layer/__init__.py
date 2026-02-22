"""
AI4UE Model Layer
AI 模型调用层 - 提供统一的 AI 接口
"""

__version__ = "1.0.0"
__author__ = "AI4UE Team"

from .config import Config
from .ai_client import AIClient
from .clients import ClaudeCodeClient

__all__ = [
    "Config",
    "AIClient",
    "ClaudeCodeClient",
]

