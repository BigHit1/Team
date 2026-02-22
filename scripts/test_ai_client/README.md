# 测试脚本

本目录包含所有测试相关的脚本。

## 测试脚本列表

### 客户端测试
- `test_claude_code_client.py` - Claude Code Client 功能测试
- `test_config.py` - 配置管理测试

### 工作流测试
- `test_standard_workflow.py` - 标准工作流测试
- `test_complete_workflow.py` - 完整工作流测试
- `test_workflow_isolation.py` - 工作流隔离机制测试
- `test_health_regen_workflow.py` - 生命恢复工作流测试

### 编排器测试
- `test_orchestrator.py` - 工作流编排器测试
- `test_orchestrator_output.py` - 编排器输出测试

### 功能测试
- `test_continue_feature.py` - 继续功能测试
- `test_multi_round_skill.py` - 多轮对话协议测试
- `test_health_regen.py` - 生命恢复功能测试

### 日志测试
- `test_logging.py` - 日志系统测试
- `test_enhanced_logging.py` - 增强日志功能测试

## 运行测试

```bash
# 运行单个测试
python scripts/test/test_standard_workflow.py

# 运行所有测试
python -m pytest scripts/test/

# 运行特定类型的测试
python -m pytest scripts/test/test_*_workflow.py
```

## 测试覆盖

- ✅ AI 客户端功能
- ✅ 工作流编排
- ✅ 多轮对话协议
- ✅ 文件隔离机制
- ✅ 日志系统
- ✅ 配置管理

