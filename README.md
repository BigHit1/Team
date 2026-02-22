# Team AI - 智能团队协作 AI 工具

> 基于 Claude 和多 Agent 编排的智能化开发协作系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-Opus_4-purple.svg)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📢 最新更新

### AI Model Layer 架构升级 (2026-02-18)

项目现已实现完整的 AI 编排系统，核心特性：

- ✅ **多 Agent 编排**: Planner → Architect → Coder → Reviewer 四阶段工作流
- ✅ **多轮对话协议**: 自动追踪任务状态，智能判断是否需要继续
- ✅ **文件权限控制**: 不同 Agent 拥有不同的文件访问权限
- ✅ **运行隔离机制**: 阶段/迭代/运行三级目录隔离
- ✅ **异步任务管理**: 支持任务监控、自动重试、进度追踪
- ✅ **技能库系统**: 可复用的协议和最佳实践

---

## 🎯 项目概述

Team AI 是一个**高度模块化的 AI 自动化开发系统**，通过多 Agent 协作完成从需求分析到代码实现的全流程。

### 核心特性

- 🧠 **智能编排**: 多阶段 Agent 工作流，每个 Agent 专注特定领域
- 🔄 **自动迭代**: 失败自动重试，支持最多 N 次迭代
- 🎭 **角色专业化**: Planner、Architect、Coder、Reviewer 等专业 Agent
- 🔒 **权限控制**: 基于角色的文件访问策略
- 📊 **实时监控**: 任务状态追踪、进度显示、日志记录
- 🎓 **技能库**: 多轮对话协议、日志最佳实践等可复用技能

---

## 🚀 快速开始

### 前置要求

- **Python**: 3.9+
- **Claude Code CLI**: 已安装并配置
- **Git**: 版本控制

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourname/team-ai.git
cd team-ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="your_api_key"
$env:ANTHROPIC_BASE_URL="your_base_url"

# 4. 测试工作流
python scripts/test_ai_client/test_standard_workflow.py
```

---

## 📖 使用指南

### 方式一：使用工作流编排器（推荐）

```python
from ai_model_layer.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient
from ai_model_layer.config import get_config

# 加载配置
config = get_config()
client_config = config.get_ai_client_config("claude_code")

# 创建客户端和编排器
client = ClaudeCodeClient(client_config)
orchestrator = WorkflowOrchestrator(client)

# 执行标准工作流
result = orchestrator.execute_workflow(
    workflow_name="standard",  # standard/quick/security
    requirement="实现用户认证功能",
    project_path="/path/to/your/project"
)
```

### 方式二：直接使用 Claude Code Client

```python
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient

# 创建客户端
client = ClaudeCodeClient({
    "api_key": "your_api_key",
    "model": "claude-opus-4",
    "max_iterations": 5
})

# 自动迭代执行任务
result = client.auto_iterate(
    requirement="创建 REST API 接口",
    project_path="/path/to/your/project",
    max_iterations=5
)
```

### 查看结果

工作流会在项目中创建隔离的工作目录：

```
YourProject/
  .claude/
    runs/
      standard_20260218_143022/    ← 本次运行
        phases/
          planning/
            iter_1/
            plan.md                ← 规划文档
          architecture/
            architecture.md        ← 架构设计
          implementation/
            implementation.md      ← 实现记录
          review/
            review.md              ← 代码审查
        docs/                      ← 生成的文档
        temp/                      ← 临时文件
```

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户层                                 │
│  Python Scripts / API / CI/CD Pipeline                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              AI Model Layer (核心)                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Orchestrator (编排器)                          │    │
│  │  - WorkflowOrchestrator: 管理多阶段工作流       │    │
│  │  - Phase: 定义工作流阶段                        │    │
│  │  - FilePolicy: 文件访问权限控制                 │    │
│  └────────────────────────────────────────────────┘    │
│                     ↓                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Agents (Agent 库)                              │    │
│  │  - planner: 需求分析和规划                      │    │
│  │  - architect: 系统架构设计                      │    │
│  │  - coder: 代码实现                              │    │
│  │  - code-reviewer: 代码审查                      │    │
│  │  - security-reviewer: 安全审查                  │    │
│  └────────────────────────────────────────────────┘    │
│                     ↓                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Clients (AI 客户端)                            │    │
│  │  - ClaudeCodeClient: Claude Code CLI 封装       │    │
│  │    • 异步任务管理                               │    │
│  │    • 自动迭代循环                               │    │
│  │    • 多轮对话协议                               │    │
│  └────────────────────────────────────────────────┘    │
│                     ↓                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Skills (技能库)                                │    │
│  │  - multi-round-protocol: 多轮对话协议           │    │
│  │  - python-logging-best-practices: 日志最佳实践  │    │
│  └────────────────────────────────────────────────┘    │
│                     ↓                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Utils (工具层)                                 │    │
│  │  - logger: 统一日志系统                         │    │
│  │  - git_wrapper: Git 操作封装                    │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                 外部服务                                  │
│  Claude API / Git / Your Project                        │
└─────────────────────────────────────────────────────────┘
```

---

### 工作流程

**标准工作流 (Standard Workflow)**

```
用户需求
   ↓
┌─────────────────────────────────────────┐
│ Phase 1: Planning (规划阶段)             │
│ Agent: planner                          │
│ - 分析需求                               │
│ - 识别风险                               │
│ - 制定实施计划                           │
│ 输出: plan.md                           │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│ Phase 2: Architecture (架构阶段)         │
│ Agent: architect                        │
│ - 读取 plan.md                          │
│ - 设计系统架构                           │
│ - 定义接口和类结构                       │
│ 输出: architecture.md                   │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│ Phase 3: Implementation (实现阶段)       │
│ Agent: coder                            │
│ - 读取 architecture.md                  │
│ - 创建/修改代码文件                      │
│ - 实现核心功能                           │
│ 输出: implementation.md + 代码文件       │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│ Phase 4: Review (审查阶段)               │
│ Agent: code-reviewer                    │
│ - 审查代码质量                           │
│ - 检查最佳实践                           │
│ - 提出改进建议                           │
│ 输出: review.md                         │
└─────────────────────────────────────────┘
   ↓
完成！
```

**每个阶段支持**：
- ✅ 自动迭代（失败自动重试）
- ✅ 状态追踪（通过多轮对话协议）
- ✅ 文件隔离（独立的工作目录）
- ✅ 权限控制（基于角色的文件访问）

---

## 🧠 AI Model Layer 核心架构

### 1. Orchestrator (编排器)

**核心类**: `WorkflowOrchestrator`

负责管理多阶段 Agent 工作流的执行：

```python
class WorkflowOrchestrator:
    def execute_workflow(
        workflow_name: str,    # 工作流名称 (standard/quick/security)
        requirement: str,      # 用户需求
        project_path: str,     # 项目路径
        dry_run: bool = False, # 是否干运行
        run_id: str = None     # 运行ID（用于隔离）
    ) -> Dict[str, Any]
```

### 2. Agents (Agent 库)

**核心类**: `AgentLibrary`

管理所有专业化的 AI Agent：

| Agent | 职责 | 权限 | 工具 |
|-------|------|------|------|
| **planner** | 需求分析、制定计划 | 只读 + 写文档 | Read, Grep, Glob, Write |
| **architect** | 系统架构设计 | 只读 + 写文档 | Read, Grep, Glob, Write |
| **coder** | 代码实现 | 读写代码 | Read, Write, Grep, Glob |
| **code-reviewer** | 代码审查 | 只读 + 写报告 | Read, Grep, Glob, Write |
| **cleaner** | 代码清理优化 | 读写代码 | Read, Write, Grep |
| **doc-updater** | 文档更新 | 读写文档 | Read, Write, Glob |
| **security-reviewer** | 安全审查 | 只读 + 写报告 | Read, Grep, Glob, Write |

---

## 🔧 配置说明

### AI 客户端配置

编辑 `config/ai_config.yaml`：

```yaml
ai_client:
  default: "claude_code"
  
  claude_code:
    api_key: "${ANTHROPIC_AUTH_TOKEN}"
    api_base_url: "${ANTHROPIC_BASE_URL}"
    cli_path: "claude"
    model: "claude-opus-4"
    max_iterations: 5
    timeout: 600
    auto_approve: true
```

### 环境变量

```bash
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="sk-ant-xxxxx"
$env:ANTHROPIC_BASE_URL="https://api.anthropic.com/"

# Linux/Mac
export ANTHROPIC_AUTH_TOKEN="sk-ant-xxxxx"
export ANTHROPIC_BASE_URL="https://api.anthropic.com/"
```

---

## 🛠️ 项目结构

```
team-ai/
├── ai_model_layer/              # 🧠 AI 模型层（核心）
│   ├── orchestrator/            # 编排器
│   │   ├── workflows/           # 工作流定义（YAML）
│   │   │   ├── standard.yaml    # 标准工作流
│   │   │   ├── quick.yaml       # 快速工作流
│   │   │   └── security.yaml    # 安全审查工作流
│   │   ├── workflow_orchestrator.py  # 工作流编排器
│   │   ├── phase.py             # 阶段定义
│   │   └── file_policy.py       # 文件权限控制
│   ├── agents/                  # Agent 库
│   │   ├── standard_agents/     # 标准 Agent 定义
│   │   │   ├── planner.md       # 规划专家
│   │   │   ├── architect.md     # 架构师
│   │   │   ├── coder.md         # 编码专家
│   │   │   ├── code-reviewer.md # 代码审查员
│   │   │   └── ...
│   │   └── agent_library.py     # Agent 库管理器
│   ├── clients/                 # AI 客户端
│   │   ├── claude_code_client.py # Claude Code CLI 客户端
│   │   └── __init__.py
│   ├── skills/                  # 技能库
│   │   ├── multi-round-protocol/ # 多轮对话协议
│   │   └── python-logging-best-practices/
│   ├── utils/                   # 工具层
│   │   ├── logger.py            # 统一日志系统
│   │   ├── git_wrapper.py       # Git 包装器
│   │   └── logging_config.py    # 日志配置
│   ├── config.py                # 配置管理器
│   ├── ai_client.py             # AI 客户端基类
│   └── __init__.py
├── config/                      # 配置文件
│   └── ai_config.yaml           # AI 客户端配置
├── scripts/                     # 脚本
│   └── test_ai_client/          # 测试脚本
├── tools/                       # 工具
│   └── git/                     # 内嵌 Git
└── logs/                        # 日志输出
```

---

## 🎓 核心概念

### 1. 工作流 (Workflow)

工作流定义了多个阶段的执行顺序和依赖关系：

- **standard**: 完整的四阶段工作流（规划→架构→实现→审查）
- **quick**: 快速工作流（跳过规划和架构）
- **security**: 安全审查工作流（增加安全审查阶段）

### 2. 阶段 (Phase)

每个阶段代表一个独立的任务单元：

- 使用特定的 Agent
- 有独立的工作目录
- 支持多次迭代
- 可以依赖前一阶段的输出

### 3. Agent

专业化的 AI 角色，每个 Agent 有：

- 专门的提示词
- 特定的工具权限
- 明确的职责范围
- 文件访问控制

### 4. 多轮对话协议

标准化的状态管理机制：

- AI 在每次响应末尾输出状态块
- 系统自动解析状态判断是否需要继续
- 支持 6 种状态（completed/continue/need_human/error/waiting/partial）
- 提供信心度、进度、文件列表等元数据

---

## 🚀 高级用法

### 自定义工作流

创建 `workflows/custom.yaml`：

```yaml
name: custom
description: 自定义工作流

phases:
  - name: analysis
    agent: planner
    requirement: "分析需求：{original_requirement}"
    max_iterations: 3
    output_file: analysis.md
  
  - name: implementation
    agent: coder
    requirement: "实现功能：{previous_output_file}"
    depends_on: analysis
    max_iterations: 10
    output_file: implementation.md
```

### 创建自定义 Agent

创建 `agents/standard_agents/my-agent.md`：

```markdown
---
name: my-agent
description: 我的自定义 Agent
model: opus
tools: ["Read", "Write", "Grep"]
---

# 我的 Agent

你是一个专门的 Agent...

## 你的职责
1. 职责 1
2. 职责 2
```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 🌟 特性亮点

- ✅ **模块化设计**: 清晰的分层架构，易于扩展
- ✅ **专业化 Agent**: 每个 Agent 专注特定领域
- ✅ **智能编排**: 灵活的工作流定义和依赖管理
- ✅ **权限控制**: 基于角色的文件访问策略
- ✅ **隔离机制**: 运行/阶段/迭代三级隔离
- ✅ **状态管理**: 标准化的多轮对话协议
- ✅ **自动重试**: 失败自动迭代，提高成功率
- ✅ **实时监控**: 任务状态追踪和进度显示
- ✅ **完整日志**: 结构化日志系统，便于调试

---

**让 AI 成为你的开发伙伴！** 🚀
