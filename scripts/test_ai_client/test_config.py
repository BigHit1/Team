"""
测试配置读取优先级
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_model_layer.config import get_config

print("="*60)
print("配置读取测试")
print("="*60)

# 显示环境变量
print("\n1. 环境变量:")
print(f"   ANTHROPIC_AUTH_TOKEN = {os.getenv('ANTHROPIC_AUTH_TOKEN', 'NOT SET')}")
print(f"   ANTHROPIC_API_KEY = {os.getenv('ANTHROPIC_API_KEY', 'NOT SET')}")
print(f"   ANTHROPIC_BASE_URL = {os.getenv('ANTHROPIC_BASE_URL', 'NOT SET')}")

# 加载配置
print("\n2. 加载配置...")
config_manager = get_config()

# 获取Claude Code配置
claude_config = config_manager.get_ai_client_config("claude_code")

print("\n3. Claude Code 配置:")
print(f"   api_key = {claude_config.get('api_key', 'NOT SET')}")
print(f"   api_base_url = {claude_config.get('api_base_url', 'NOT SET')}")
print(f"   model = {claude_config.get('model', 'NOT SET')}")
print(f"   cli_path = {claude_config.get('cli_path', 'NOT SET')}")

print("\n4. 完整配置:")
for key, value in claude_config.items():
    if key in ['api_key', 'api_base_url']:
        # 只显示前20个字符
        display_value = str(value)[:20] + "..." if value and len(str(value)) > 20 else value
        print(f"   {key} = {display_value}")
    else:
        print(f"   {key} = {value}")

print("\n" + "="*60)

