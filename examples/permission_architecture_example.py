"""
新权限架构使用示例
演示如何使用 Workspace 和 AccessPolicy
"""

from pathlib import Path
from ai_model_layer.orchestrator.workspace import Workspace, WorkspaceZone
from ai_model_layer.orchestrator.access_policy import AccessPolicy, Permission
from ai_model_layer.agents.agent_library import AgentLibrary


def example_1_workspace_usage():
    """示例 1：使用 Workspace 管理工作区"""
    print("=" * 60)
    print("示例 1：Workspace 使用")
    print("=" * 60)
    
    # 创建工作区
    workspace = Workspace(
        project_path="/path/to/project",
        run_id="standard_20260223_120000"
    )
    
    # 获取各个区域的路径
    print(f"输出区: {workspace.get_zone_path(WorkspaceZone.OUTPUT)}")
    print(f"临时区: {workspace.get_zone_path(WorkspaceZone.TEMP)}")
    print(f"文档区: {workspace.get_zone_path(WorkspaceZone.DOCS)}")
    print(f"图表区: {workspace.get_zone_path(WorkspaceZone.DIAGRAMS)}")
    print(f"阶段区: {workspace.get_zone_path(WorkspaceZone.PHASES)}")
    print(f"项目区: {workspace.get_zone_path(WorkspaceZone.PROJECT)}")
    
    # 获取文档子目录
    print(f"\n文档子目录:")
    print(f"  规划文档: {workspace.get_doc_subdir('plans')}")
    print(f"  架构文档: {workspace.get_doc_subdir('architecture')}")
    print(f"  审查报告: {workspace.get_doc_subdir('reviews')}")
    
    # 获取临时子目录（按阶段和迭代隔离）
    print(f"\n临时子目录:")
    print(f"  规划临时: {workspace.get_temp_subdir('planning', iteration=1)}")
    print(f"  架构临时: {workspace.get_temp_subdir('architecture', iteration=1)}")
    
    # 获取阶段输出路径
    print(f"\n阶段输出:")
    print(f"  规划输出: {workspace.get_phase_output_path('planning', 'plan.md', iteration=1)}")
    print(f"  架构输出: {workspace.get_phase_output_path('architecture', 'architecture.md', iteration=1)}")
    
    # 创建目录
    workspace.ensure_directories()
    print(f"\n✓ 所有目录已创建")
    
    # 获取工作区结构信息
    print(f"\n工作区结构信息:")
    print(workspace.get_structure_info())


def example_2_access_policy():
    """示例 2：使用 AccessPolicy 检查权限"""
    print("\n" + "=" * 60)
    print("示例 2：AccessPolicy 使用")
    print("=" * 60)
    
    # 创建工作区和访问策略
    workspace = Workspace(
        project_path="/path/to/project",
        run_id="standard_20260223_120000"
    )
    access_policy = AccessPolicy(workspace)
    
    # 模拟 Agent 配置
    planner_config = {
        "name": "planner",
        "read_zones": ["*"],
        "write_zones": [
            {"zone": "docs", "subdir": "plans"},
            {"zone": "temp", "subdir": "planning"}
        ],
        "restrictions": ["创建或修改代码文件"],
        "guidance": "你的主要输出应该在回复中。"
    }
    
    coder_config = {
        "name": "coder",
        "read_zones": ["*"],
        "write_zones": [
            "project",
            {"zone": "temp", "subdir": "implementation"}
        ],
        "restrictions": ["修改 .claude/ 工作区目录下的文件"],
        "guidance": "你可以创建和修改项目代码文件。"
    }
    
    # 测试权限
    print("\n测试 Planner 权限:")
    
    # Planner 可以写入文档区
    doc_path = workspace.get_doc_subdir("plans") / "plan.md"
    can_write = access_policy.check_access(
        planner_config,
        doc_path,
        Permission.WRITE,
        phase_name="planning",
        iteration=1
    )
    print(f"  写入 {doc_path}: {'✓ 允许' if can_write else '✗ 拒绝'}")
    
    # Planner 不能写入项目代码
    code_path = Path("/path/to/project/src/main.py")
    can_write = access_policy.check_access(
        planner_config,
        code_path,
        Permission.WRITE,
        phase_name="planning",
        iteration=1
    )
    print(f"  写入 {code_path}: {'✓ 允许' if can_write else '✗ 拒绝'}")
    
    print("\n测试 Coder 权限:")
    
    # Coder 可以写入项目代码
    can_write = access_policy.check_access(
        coder_config,
        code_path,
        Permission.WRITE,
        phase_name="implementation",
        iteration=1
    )
    print(f"  写入 {code_path}: {'✓ 允许' if can_write else '✗ 拒绝'}")
    
    # Coder 不能写入工作区目录
    workspace_path = workspace.workspace_root / "config.yaml"
    can_write = access_policy.check_access(
        coder_config,
        workspace_path,
        Permission.WRITE,
        phase_name="implementation",
        iteration=1
    )
    print(f"  写入 {workspace_path}: {'✓ 允许' if can_write else '✗ 拒绝'}")
    
    # 获取可写路径列表
    print("\nPlanner 可写路径:")
    writable_paths = access_policy.get_writable_paths(
        planner_config,
        phase_name="planning",
        iteration=1
    )
    for path in writable_paths:
        print(f"  - {path}")
    
    print("\nCoder 可写路径:")
    writable_paths = access_policy.get_writable_paths(
        coder_config,
        phase_name="implementation",
        iteration=1
    )
    for path in writable_paths:
        print(f"  - {path}")


def example_3_agent_library():
    """示例 3：从 Agent 库加载权限配置"""
    print("\n" + "=" * 60)
    print("示例 3：从 Agent 库加载配置")
    print("=" * 60)
    
    # 加载 Agent 库
    agent_library = AgentLibrary()
    
    # 列出所有 Agent
    print("\n可用的 Agents:")
    for name, description in agent_library.list_agents().items():
        print(f"  - {name}: {description}")
    
    # 获取 Agent 配置
    print("\n获取 Planner 配置:")
    planner = agent_library.get_agent("planner")
    if planner:
        print(f"  名称: {planner['name']}")
        print(f"  描述: {planner['description']}")
        print(f"  模型: {planner['model']}")
        print(f"  工具: {planner['tools']}")
        print(f"  读取区域: {planner['read_zones']}")
        print(f"  写入区域: {planner['write_zones']}")
        print(f"  限制: {planner['restrictions']}")
        print(f"  指导: {planner['guidance']}")


def example_4_complete_workflow():
    """示例 4：完整的工作流示例"""
    print("\n" + "=" * 60)
    print("示例 4：完整工作流")
    print("=" * 60)
    
    # 1. 创建工作区
    workspace = Workspace(
        project_path="/path/to/project",
        run_id="standard_20260223_120000"
    )
    workspace.ensure_directories()
    
    # 2. 创建访问策略
    access_policy = AccessPolicy(workspace)
    
    # 3. 加载 Agent 库
    agent_library = AgentLibrary()
    
    # 4. 模拟工作流执行
    phases = ["planning", "architecture", "implementation", "review"]
    
    for phase_name in phases:
        print(f"\n执行阶段: {phase_name}")
        
        # 根据阶段选择 Agent
        if phase_name == "planning":
            agent_name = "planner"
        elif phase_name == "architecture":
            agent_name = "architect"
        elif phase_name == "implementation":
            agent_name = "coder"
        else:
            agent_name = "code-reviewer"
        
        # 获取 Agent 配置
        agent_config = agent_library.get_agent(agent_name)
        if not agent_config:
            print(f"  ✗ Agent 不存在: {agent_name}")
            continue
        
        print(f"  Agent: {agent_name}")
        
        # 获取文件操作指导
        guidance = access_policy.get_guidance(agent_config)
        print(f"  权限指导:")
        for line in guidance.split('\n')[:10]:  # 只显示前10行
            if line.strip():
                print(f"    {line}")
        
        # 获取可写路径
        writable_paths = access_policy.get_writable_paths(
            agent_config,
            phase_name=phase_name,
            iteration=1
        )
        print(f"  可写路径: {len(writable_paths)} 个")
        
        # 获取阶段输出路径
        output_path = workspace.get_phase_output_path(
            phase_name,
            f"{phase_name}.md",
            iteration=1
        )
        print(f"  输出路径: {output_path}")


if __name__ == "__main__":
    # 运行所有示例
    example_1_workspace_usage()
    example_2_access_policy()
    example_3_agent_library()
    example_4_complete_workflow()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成！")
    print("=" * 60)

