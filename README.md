# AI4UE - AI 驱动的 UE5 自动化开发流水线

> 基于 Claude Code CLI 和多 Agent 编排的智能化 UE5 开发系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![UE5](https://img.shields.io/badge/UE5-5.3+-orange.svg)](https://www.unrealengine.com/)
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

📖 详见 [架构文档](docs/ARCHITECTURE.md) | [AI Model Layer 详解](#-ai-model-layer-核心架构)

---

## 🎯 项目概述

AI4UE 是一个**高度模块化的 AI 自动化开发系统**，通过多 Agent 协作完成从需求分析到代码实现的全流程。

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
- **UE5**: 5.3+ (可选，用于 UE5 项目开发)

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourname/AI4UE_Plugin.git
cd AI4UE_Plugin

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="your_api_key"
$env:ANTHROPIC_BASE_URL="your_base_url"

# 4. 测试工作流
python scripts/test/test_standard_workflow.py
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
    requirement="为 Lyra 添加生命恢复能力",
    project_path="D:/UE5Projects/LyraStarterGame"
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
    requirement="创建武器系统",
    project_path="D:/UE5Projects/MyGame",
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
│  Python Scripts / API / Jenkins Pipeline                │
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
│  │  - ue5-code-guide: UE5 代码实现                 │    │
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
│  Claude API / Git / UE5 Project                         │
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
│ Agent: ue5-code-guide                   │
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

**工作流定义** (YAML 格式):

```yaml
# workflows/standard.yaml
name: standard
description: 标准开发工作流

phases:
  - name: planning
    agent: planner
    requirement: "分析需求：{original_requirement}"
    max_iterations: 5
    output_file: plan.md
  
  - name: architecture
    agent: architect
    requirement: "基于计划设计架构：{previous_output_file}"
    depends_on: planning
    max_iterations: 5
    output_file: architecture.md
```

**特性**：
- 支持阶段依赖 (`depends_on`)
- 支持模板变量 (`{previous_output_file}`)
- 支持运行隔离 (每次运行独立目录)
- 支持迭代隔离 (每次迭代独立目录)

### 2. Agents (Agent 库)

**核心类**: `AgentLibrary`

管理所有专业化的 AI Agent：

| Agent | 职责 | 权限 | 工具 |
|-------|------|------|------|
| **planner** | 需求分析、制定计划 | 只读 + 写文档 | Read, Grep, Glob, Write |
| **architect** | 系统架构设计 | 只读 + 写文档 | Read, Grep, Glob, Write |
| **ue5-code-guide** | UE5 代码实现 | 读写代码 | Read, Write, Grep, Glob |
| **code-reviewer** | 代码审查 | 只读 + 写报告 | Read, Grep, Glob, Write |
| **cleaner** | 代码清理优化 | 读写代码 | Read, Write, Grep |
| **doc-updater** | 文档更新 | 读写文档 | Read, Write, Glob |
| **security-reviewer** | 安全审查 | 只读 + 写报告 | Read, Grep, Glob, Write |

**Agent 定义格式**:

```markdown
---
name: planner
description: 规划专家
model: opus
tools: ["Read", "Grep", "Glob", "Write"]
---

# 规划专家 (Planner Agent)

你是一个经验丰富的软件规划专家...

## 你的职责
1. 需求分析
2. 风险识别
3. 步骤分解
...
```

### 3. Clients (AI 客户端)

**核心类**: `ClaudeCodeClient`

封装 Claude Code CLI，提供高级功能：

```python
class ClaudeCodeClient:
    # 异步任务管理
    def start_task(requirement, project_path) -> ClaudeCodeTask
    def check_task_status(task_id) -> Dict
    def wait_for_task(task_id, timeout) -> AIResponse
    
    # 自动迭代循环
    def auto_iterate(
        requirement: str,
        project_path: str,
        max_iterations: int = 5,
        validation_func: Callable = None
    ) -> AIResponse
```

**特性**：
- ✅ 异步任务管理（启动后可监控进度）
- ✅ 自动迭代循环（失败自动重试）
- ✅ 多轮对话协议（解析状态块）
- ✅ 环境变量管理（自动设置 API 密钥）
- ✅ 索引目录支持（访问 UE5 引擎代码）

### 4. Skills (技能库)

**多轮对话协议** (`multi-round-protocol`)

让 AI 在每次响应末尾输出结构化状态：

```yaml
---TASK_STATUS---
status: completed          # completed/continue/need_human/error/waiting/partial
reason: 任务完成
confidence: 0.9            # 信心度 0.0-1.0
progress: 1.0              # 进度 0.0-1.0
files_modified: [...]      # 修改的文件列表
warnings: [...]            # 警告信息
---END_STATUS---
```

**6种状态**：
- `completed`: 任务完成（信心度 0.8-1.0）
- `continue`: 需要继续（任务太大，分步执行）
- `need_human`: 需要人工介入（决策/许可/澄清）
- `error`: 遇到错误（需要修复）
- `waiting`: 等待中（等待外部操作）
- `partial`: 部分完成（有警告，信心度 0.5-0.8）

### 5. FilePolicy (文件权限控制)

**核心类**: `FilePolicy`

基于角色控制 Agent 的文件访问权限：

```python
class FilePolicy:
    def get_allowed_write_paths(
        agent_role: str,    # Agent 角色
        phase_name: str,    # 阶段名称
        iteration: int      # 迭代次数
    ) -> List[Path]
```

**目录隔离结构**：

```
.claude/
└── runs/
    └── {run_id}/              # 运行隔离
        ├── phases/            # 阶段输出
        │   ├── planning/
        │   │   ├── iter_1/    # 迭代隔离
        │   │   ├── iter_2/
        │   │   └── plan.md
        │   ├── architecture/
        │   └── implementation/
        ├── docs/              # 文档目录
        │   ├── plans/
        │   └── architecture/
        ├── temp/              # 临时文件
        └── diagrams/          # 图表文件
```

**权限示例**：
- `planner`: 可写 `docs/plans/`, `temp/planning/`
- `architect`: 可写 `docs/architecture/`, `diagrams/`, `temp/architecture/`
- `ue5-code-guide`: 可写项目源代码目录
- `code-reviewer`: 只读代码，可写 `docs/reviews/`

### 6. Utils (工具层)

**统一日志系统** (`logger.py`)

```python
from ai_model_layer.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("任务开始", extra={"task_id": "123", "phase": "planning"})
```

**特性**：
- 彩色控制台输出
- 文件日志（自动轮转）
- JSON 格式日志
- 上下文信息支持

**Git 包装器** (`git_wrapper.py`)

```python
from ai_model_layer.utils.git_wrapper import get_git_wrapper

git = get_git_wrapper()
git.commit("实现功能 X")
changes = git.get_changes()
```

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
    index_directories:
      - "F:/UE5/LyraStarterGame"    # 项目目录
      - "F:/UE5/UE_5.4"              # 引擎目录
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

## 📚 文档

### 核心文档
- [架构文档](docs/ARCHITECTURE.md) - 完整的系统架构说明
- [Agent 编排指南](docs/AGENT_ORCHESTRATION_GUIDE.md) - 工作流编排详解
- [多轮对话协议](docs/MULTI_ROUND_PROTOCOL.md) - 状态管理协议
- [日志系统指南](docs/LOGGING_GUIDE.md) - 日志使用说明

### 使用指南
- [配置指南](docs/CONFIGURATION_GUIDE.md) - 详细配置说明
- [Claude Code CLI 指南](docs/claude_code_cli_guide.md) - CLI 使用方法
- [文件权限设计](docs/file_policy_design.md) - 权限控制机制

### 示例代码
- [Claude Code Client 示例](examples/claude_code_client_examples.py) - 客户端使用示例
- [日志示例](examples/logging_examples.py) - 日志系统示例

---

## 🛠️ 项目结构

```
AI4UE_Plugin/
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
│   │   │   ├── ue5-code-guide.md # UE5 编码专家
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
│   ├── ai_config.yaml           # AI 客户端配置
│   ├── ue5_project_config.yaml  # UE5 项目配置
│   └── jenkins_config.yaml      # Jenkins 配置
├── scripts/                     # 脚本
│   ├── test/                    # 测试脚本
│   │   ├── test_standard_workflow.py    # 测试标准工作流
│   │   ├── test_claude_code_client.py   # 测试客户端
│   │   ├── test_orchestrator.py         # 测试编排器
│   │   └── ...
│   ├── ai_coding_auto.py        # AI 自动化编码
│   ├── workflow.py              # 工作流执行脚本
│   ├── pack_hotupdate.py        # 打包热更新
│   └── push_patch.py            # 推送补丁
├── examples/                    # 示例代码
│   ├── claude_code_client_examples.py
│   └── logging_examples.py
├── docs/                        # 文档
│   ├── ARCHITECTURE.md          # 架构文档
│   ├── AGENT_ORCHESTRATION_GUIDE.md
│   ├── MULTI_ROUND_PROTOCOL.md
│   └── ...
├── requirements/                # 需求文档示例
│   └── examples/
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
- 系统自动解析状态判断是否继续
- 支持 6 种状态（completed/continue/need_human/error/waiting/partial）
- 提供信心度、进度、文件列表等元数据

### 5. 隔离机制

三级目录隔离确保任务独立性：

- **运行隔离**: 每次运行有独立的 run_id
- **阶段隔离**: 每个阶段有独立的输出目录
- **迭代隔离**: 每次迭代有独立的临时目录

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
    agent: ue5-code-guide
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

### 扩展 ClaudeCodeClient

```python
from ai_model_layer.clients.claude_code_client import ClaudeCodeClient

class MyCustomClient(ClaudeCodeClient):
    def custom_method(self):
        # 自定义逻辑
        pass
```

---

## 🔍 故障排查

### 常见问题

**Q: 任务一直显示 "running" 状态？**

A: 检查 Claude Code CLI 是否正常运行，查看日志文件 `logs/ai4ue.log`

**Q: Agent 无法访问某些文件？**

A: 检查 FilePolicy 配置，确保 Agent 有相应的文件权限

**Q: 工作流执行失败？**

A: 查看 `.claude/runs/{run_id}/phases/` 目录下的输出文件，检查错误信息

**Q: 如何调试多轮对话协议？**

A: 在 AI 响应中查找 `---TASK_STATUS---` 块，检查状态和原因

### 日志查看

```bash
# 查看实时日志
tail -f logs/ai4ue.log

# 查看 JSON 格式日志
cat logs/ai4ue.json.log | jq

# 查看错误日志
cat logs/ai4ue.error.log
```

---

## 📊 性能优化

### 1. 使用索引目录

在配置中添加常用目录，加速 AI 代码理解：

```yaml
index_directories:
  - "F:/UE5/LyraStarterGame"
  - "F:/UE5/UE_5.4/Engine/Source"
```

### 2. 调整迭代次数

根据任务复杂度调整 `max_iterations`：

- 简单任务: 2-3 次
- 中等复杂: 5 次
- 复杂重构: 10 次

### 3. 使用 dry_run 模式

测试工作流配置而不实际执行：

```python
result = orchestrator.execute_workflow(
    workflow_name="standard",
    requirement="测试需求",
    project_path="/path/to/project",
    dry_run=True  # 不实际执行
)
```

### 4. 继续上次运行

使用 `use_latest=True` 继续上次未完成的运行：

```python
result = orchestrator.execute_workflow(
    workflow_name="standard",
    requirement="继续上次任务",
    project_path="/path/to/project",
    use_latest=True  # 使用最新的 run_id
)
```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献方向

- 🤖 添加新的 Agent（如测试专家、性能优化专家）
- 🔄 创建新的工作流模板
- 🎓 贡献新的 Skill（如 UE5 最佳实践）
- 📖 改进文档和示例
- 🐛 修复 Bug 和改进性能

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- **Anthropic** - Claude AI 和 Claude Code CLI
- **Epic Games** - UE5 引擎
- **Python 社区** - 优秀的开源库

---

## 📞 联系方式

- 问题反馈: [GitHub Issues](https://github.com/yourname/AI4UE_Plugin/issues)
- 邮箱: your.email@example.com

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

**让 AI 成为你的 UE5 开发伙伴！** 🚀
