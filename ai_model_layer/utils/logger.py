"""
统一日志系统
提供结构化、分级、可配置的日志功能

日志规范：
1. 使用 Python 标准 logging 模块
2. 支持多种输出目标（控制台、文件、JSON）
3. 结构化日志格式，便于分析和监控
4. 按模块分级管理日志
5. 支持日志轮转和归档
6. 包含上下文信息（任务ID、用户、时间戳等）
"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import traceback


# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 基础信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加上下文信息
        if self.include_context and hasattr(record, 'context'):
            log_data["context"] = record.context
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'lineno', 'module', 'msecs', 'message',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'context']:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """彩色控制台格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    # 日志级别图标
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠',
        'ERROR': '✗',
        'CRITICAL': '🔥'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 获取颜色和图标
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        icon = self.ICONS.get(record.levelname, '•')
        reset = self.COLORS['RESET']
        
        # 时间戳
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # 构建日志消息
        message = record.getMessage()
        
        # 基础格式
        log_line = f"{color}{icon} [{timestamp}] {record.levelname:8s}{reset} {message}"
        
        # 添加位置信息（DEBUG 级别）
        if record.levelno == logging.DEBUG:
            location = f"{record.module}.{record.funcName}:{record.lineno}"
            log_line += f" {reset}\033[90m({location}){reset}"
        
        # 添加异常信息
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"
        
        return log_line


class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_dir: Optional[Path] = None
        self.console_level = logging.INFO
        self.file_level = logging.DEBUG
        self.enable_json = False
        self.enable_console = True
        self.enable_file = True
        
        self._initialized = True
    
    def setup(
        self,
        log_dir: Optional[str] = None,
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        enable_json: bool = False,
        enable_console: bool = True,
        enable_file: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        配置日志系统
        
        Args:
            log_dir: 日志目录
            console_level: 控制台日志级别
            file_level: 文件日志级别
            enable_json: 是否启用 JSON 格式日志
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出
            max_bytes: 单个日志文件最大大小
            backup_count: 保留的日志文件数量
        """
        self.console_level = LOG_LEVELS.get(console_level.upper(), logging.INFO)
        self.file_level = LOG_LEVELS.get(file_level.upper(), logging.DEBUG)
        self.enable_json = enable_json
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # 设置日志目录
        if log_dir:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()
        
        # 控制台处理器
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.console_level)
            console_handler.setFormatter(ColoredConsoleFormatter())
            root_logger.addHandler(console_handler)
        
        # 文件处理器
        if self.enable_file and self.log_dir:
            # 普通日志文件
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "ai4ue.log",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.file_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
            # JSON 日志文件（可选）
            if self.enable_json:
                json_handler = logging.handlers.RotatingFileHandler(
                    self.log_dir / "ai4ue.json.log",
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                json_handler.setLevel(self.file_level)
                json_handler.setFormatter(StructuredFormatter())
                root_logger.addHandler(json_handler)
            
            # 错误日志文件
            error_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "ai4ue.error.log",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            root_logger.addHandler(error_handler)
    
    def get_logger(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> logging.Logger:
        """
        获取日志器
        
        Args:
            name: 日志器名称（通常是模块名）
            context: 上下文信息
        
        Returns:
            日志器实例
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # 添加上下文适配器
            if context:
                logger = ContextAdapter(logger, context)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def add_context(self, logger: logging.Logger, context: Dict[str, Any]) -> logging.LoggerAdapter:
        """为日志器添加上下文"""
        return ContextAdapter(logger, context)


class ContextAdapter(logging.LoggerAdapter):
    """上下文适配器 - 为日志添加上下文信息"""
    
    def process(self, msg, kwargs):
        """处理日志消息，添加上下文"""
        # 将上下文添加到 extra 中
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra']['context'] = self.extra
        
        return msg, kwargs


# 全局日志管理器实例
_logger_manager = LoggerManager()


def setup_logging(
    log_dir: Optional[str] = None,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    enable_json: bool = False,
    enable_console: bool = True,
    enable_file: bool = True,
    **kwargs
):
    """
    配置全局日志系统
    
    Args:
        log_dir: 日志目录
        console_level: 控制台日志级别
        file_level: 文件日志级别
        enable_json: 是否启用 JSON 格式
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
        **kwargs: 其他配置参数
    """
    _logger_manager.setup(
        log_dir=log_dir,
        console_level=console_level,
        file_level=file_level,
        enable_json=enable_json,
        enable_console=enable_console,
        enable_file=enable_file,
        **kwargs
    )


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    获取日志器
    
    Args:
        name: 日志器名称（建议使用 __name__）
        context: 上下文信息（如 task_id, user_id 等）
    
    Returns:
        日志器实例
    
    Example:
        >>> logger = get_logger(__name__, {"task_id": "task_123"})
        >>> logger.info("任务开始执行")
    """
    return _logger_manager.get_logger(name, context)


def add_context(logger: logging.Logger, context: Dict[str, Any]) -> logging.LoggerAdapter:
    """
    为现有日志器添加上下文
    
    Args:
        logger: 日志器实例
        context: 上下文信息
    
    Returns:
        带上下文的日志适配器
    
    Example:
        >>> logger = get_logger(__name__)
        >>> task_logger = add_context(logger, {"task_id": "task_123"})
        >>> task_logger.info("任务执行中")
    """
    return _logger_manager.add_context(logger, context)


# 便捷函数
def debug(msg: str, *args, **kwargs):
    """记录 DEBUG 级别日志"""
    logging.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """记录 INFO 级别日志"""
    logging.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """记录 WARNING 级别日志"""
    logging.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """记录 ERROR 级别日志"""
    logging.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """记录 CRITICAL 级别日志"""
    logging.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """记录异常信息"""
    logging.exception(msg, *args, **kwargs)

