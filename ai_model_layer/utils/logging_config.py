"""
日志配置预设
提供不同环境的日志配置
"""

from typing import Dict, Any


def get_development_config() -> Dict[str, Any]:
    """开发环境日志配置"""
    return {
        "log_dir": "logs",
        "console_level": "DEBUG",
        "file_level": "DEBUG",
        "enable_json": False,
        "enable_console": True,
        "enable_file": True,
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 3
    }


def get_production_config() -> Dict[str, Any]:
    """生产环境日志配置"""
    return {
        "log_dir": "/var/log/ai4ue",
        "console_level": "INFO",
        "file_level": "INFO",
        "enable_json": True,
        "enable_console": True,
        "enable_file": True,
        "max_bytes": 50 * 1024 * 1024,  # 50MB
        "backup_count": 10
    }


def get_testing_config() -> Dict[str, Any]:
    """测试环境日志配置"""
    return {
        "log_dir": "test_logs",
        "console_level": "WARNING",
        "file_level": "DEBUG",
        "enable_json": False,
        "enable_console": True,
        "enable_file": True,
        "max_bytes": 5 * 1024 * 1024,  # 5MB
        "backup_count": 2
    }


def get_config_by_env(env: str = "development") -> Dict[str, Any]:
    """
    根据环境获取日志配置
    
    Args:
        env: 环境名称 (development, production, testing)
    
    Returns:
        日志配置字典
    """
    configs = {
        "development": get_development_config(),
        "production": get_production_config(),
        "testing": get_testing_config()
    }
    
    return configs.get(env.lower(), get_development_config())

