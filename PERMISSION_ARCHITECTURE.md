# 权限架构重构说明

## 重构目标

将 Agent 角色和文件策略解耦，实现更灵活、更优雅的权限管理系统。

## 旧架构的问题

### 问题 1：耦合过紧
```python
# file_policy.py 中硬编码了 Agent 角色
if agent_role == "planner":
    allowed_paths.extend([...])
elif agent_role == "architect":
    allowed_paths.extend([...])
```

**问题**：
- Agent 和文件策略紧密耦合
- 添加新 Agent 需要修改 `file_policy.py`
- 无法灵活配置 Agent 权限

### 问题 2：职责不清
`FilePolicy` 既负责定义目录结构，又负责权限判断，违反单一职责原则。

## 新架构设计

### 三层分离

```
┌─────────────────────────────────────────┐
│  Agent 配置 (agent.md)                   │
│  - 声明自己需要的权限                     │
│  - read_zones: ["*"]                    │
│  - write_zones: [...]                   │
│  - restrictions: [...]                  │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│  AccessPolicy (access_policy.py)        │
│  - 权限匹配和判断                         │
│  - 根据 Agent 配置检查访问权限            │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│  Workspace (workspace.py)               │
│  - 定义工作区结构                         │
│  - 管理目录和区域                         │
└─────────────────────────────────────────┘
```

## 核心组件

### 1. Workspace - 工作区管理器

**职责**：定义和管理 AI 工程的目录结构

```python
class Workspace:
    """工作区管理器 - 只负责目录结构"""
    
    def __init__(self, project_path: str, run_id: Optional[str] = None):
        # 定义区域
        self._zones = {
            WorkspaceZone.OUTPUT: self.run_root / "output",
            WorkspaceZone.TEMP: self.run_root / "temp",
            WorkspaceZone.DOCS: self.run_root / "docs",
            WorkspaceZone.DIAGRAMS: self.run_root / "diagrams",
            WorkspaceZone.PHASES: self.run_root / "phases",
            WorkspaceZone.PROJECT: self.project_path
        }
```

**区域类型**：
- `OUTPUT` - 输出区：最终产物
- `TEMP` - 临时区：过程文件（按阶段和迭代隔离）
- `DOCS` - 文档区：文档和报告（plans/architecture/reviews/reports）
- `DIAGRAMS` - 图表区：架构图、流程图
- `PHASES` - 阶段区：各阶段的输出
- `PROJECT` - 项目区：项目源代码

### 2. AccessPolicy - 访问策略

**职责**：根据 Agent 配置和工作区结构判断权限

```python
class AccessPolicy:
    """访问策略 - 权限匹配和判断"""
    
    def check_access(
        self,
        agent_config: Dict[str, Any],  # Agent 的权限配置
        file_path: Path,
        permission: Permission,
        phase_name: Optional[str] = None,
        iteration: int = 1
    ) -> bool:
        """检查 Agent 是否有权限访问指定文件"""
```

**权限类型**：
- `READ` - 读取权限
- `WRITE` - 写入权限
- `DELETE` - 删除权限

### 3. Agent 配置 - 权限声明

**职责**：Agent 声明自己需要的权限

```yaml
---
name: planner
description: 规划专家
model: opus
tools: ["Read", "Grep", "Glob", "Write"]

# 权限配置
read_zones: ["*"]  # 可以读取所有区域
write_zones:
  - zone: "docs"
    subdir: "plans"
  - zone: "temp"
    subdir: "planning"
restrictions:
  - "创建或修改代码文件"
  - "修改项目源代码"
guidance: "你的主要输出应该在回复中，详细的补充文档可以创建到 docs/plans/ 目录。"
---
```

## 权限配置示例

### Planner（规划专家）
```yaml
read_zones: ["*"]  # 读取所有
write_zones:
  - zone: "docs"
    subdir: "plans"
  - zone: "temp"
    subdir: "planning"
```

### Architect（架构师）
```yaml
read_zones: ["*"]
write_zones:
  - zone: "docs"
    subdir: "architecture"
  - zone: "diagrams"
  - zone: "temp"
    subdir: "architecture"
```

### Coder（编码专家）
```yaml
read_zones: ["*"]
write_zones:
  - "project"  # 可以写入项目源代码
  - zone: "temp"
    subdir: "implementation"
restrictions:
  - "修改 .claude/ 工作区目录下的文件"
```

### Code Reviewer（代码审查员）
```yaml
read_zones: ["*"]
write_zones:
  - zone: "docs"
    subdir: "reviews"
  - zone: "temp"
    subdir: "reviews"
restrictions:
  - "创建或修改代码文件"
```

## 工作区目录结构

```
project/
├── .claude/
│   └── runs/
│       └── {run_id}/
│           ├── output/          # 输出区：最终产物
│           ├── temp/            # 临时区：过程文件
│           │   ├── planning/
│           │   │   └── iter_1/
│           │   ├── architecture/
│           │   │   └── iter_1/
│           │   └── implementation/
│           │       └── iter_1/
│           ├── docs/            # 文档区
│           │   ├── plans/
│           │   ├── architecture/
│           │   ├── reviews/
│           │   └── reports/
│           ├── diagrams/        # 图表区
│           └── phases/          # 阶段区
│               ├── plan.md
│               ├── architecture.md
│               └── implementation.md
└── src/                         # 项目区（源代码）
```

## 优势

### 1. 解耦
- Agent 配置独立于工作区结构
- 添加新 Agent 不需要修改核心代码
- 工作区结构变更不影响 Agent 定义

### 2. 灵活
- Agent 可以声明式配置权限
- 支持细粒度的权限控制（区域 + 子目录）
- 易于扩展新的区域类型

### 3. 清晰
- 职责分离：Workspace 管结构，AccessPolicy 管权限，Agent 管需求
- 配置即文档：从 Agent 配置就能看出权限
- 易于理解和维护

### 4. 安全
- 默认拒绝策略
- 显式声明权限
- 工作区隔离（.claude/ 目录保护）

## 迁移指南

### 旧代码
```python
# 硬编码在 file_policy.py 中
if agent_role == "planner":
    allowed_paths.extend([
        self.docs_dir / "plans",
        self.temp_dir / "planning"
    ])
```

### 新代码
```yaml
# 在 planner.md 中声明
write_zones:
  - zone: "docs"
    subdir: "plans"
  - zone: "temp"
    subdir: "planning"
```

## 扩展示例

### 添加新的 Agent

1. 创建 `agents/standard_agents/my-agent.md`
2. 声明权限配置
3. 无需修改任何核心代码

```yaml
---
name: my-agent
description: 我的自定义 Agent
model: opus
tools: ["Read", "Write"]

read_zones: ["*"]
write_zones:
  - zone: "docs"
    subdir: "my-reports"
  - zone: "temp"
    subdir: "my-temp"
restrictions:
  - "修改项目源代码"
guidance: "你可以创建报告到 docs/my-reports/ 目录。"
---
```

### 添加新的工作区区域

1. 在 `workspace.py` 中添加新的 `WorkspaceZone`
2. Agent 配置中引用新区域
3. 无需修改权限判断逻辑

```python
class WorkspaceZone(Enum):
    # ... 现有区域 ...
    TESTS = "tests"  # 新增：测试区
```

## 总结

新架构实现了真正的关注点分离：

- **Workspace**：我定义有哪些区域
- **Agent**：我需要访问哪些区域
- **AccessPolicy**：我来判断是否允许

这种设计更加优雅、灵活、易于维护和扩展。

