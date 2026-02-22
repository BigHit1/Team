"""
工作流编排器
负责执行多阶段 Agent 工作流
"""

import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

from .phase import Phase
from .workspace import Workspace
from .access_policy import AccessPolicy
from ..agents.agent_library import AgentLibrary
from ..clients.claude_code_client import ClaudeCodeClient, TaskStatus
from ..utils.logger import get_logger

# 获取日志器
logger = get_logger(__name__)


class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(
        self,
        client: Optional[ClaudeCodeClient] = None,
        agent_library: Optional[AgentLibrary] = None
    ):
        """
        初始化编排器
        
        Args:
            client: Claude Code 客户端（可选，dry_run 模式不需要）
            agent_library: Agent 库（可选，默认使用标准库）
        """
        self.client = client
        self.agent_library = agent_library or AgentLibrary()
        self.workspace = None  # 将在执行时初始化
        self.access_policy = None  # 将在执行时初始化
        
        # 跟踪每个阶段的执行次数（用于迭代隔离）
        self.phase_execution_count: Dict[str, int] = {}
        
        # 当前 workflow run ID（用于多次运行隔离）
        self.current_run_id: Optional[str] = None
    
    def execute_workflow(
        self,
        workflow_name: str,
        requirement: str,
        project_path: str = None,
        dry_run: bool = False,
        run_id: Optional[str] = None,
        use_latest: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行预定义工作流
        
        Args:
            workflow_name: 工作流名称（如 'standard', 'quick', 'security'）
            requirement: 原始需求
            project_path: 项目路径（dry_run 模式可选）
            dry_run: 是否为干运行模式（不实际执行）
            run_id: 运行ID（可选，用于标识本次运行）
            use_latest: 是否使用最新的运行（不创建新的 run_id）
            **kwargs: 额外参数
        
        Returns:
            工作流执行结果
        """
        # 加载工作流定义
        workflow = self._load_workflow(workflow_name)
        
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_name}")
        
        # 生成或使用 run_id
        if use_latest and project_path:
            # 使用最新的 run_id（继续上次运行）
            self.current_run_id = self._get_latest_run_id(project_path, workflow_name)
            if not self.current_run_id:
                # 如果没有历史运行，创建新的
                self.current_run_id = self._generate_run_id(workflow_name)
                logger.info(f"没有找到历史运行，创建新的 run_id: {self.current_run_id}")
            else:
                logger.info(f"继续使用最新的 run_id: {self.current_run_id}")
        elif run_id:
            # 使用指定的 run_id
            self.current_run_id = run_id
            logger.info(f"使用指定的 run_id: {self.current_run_id}")
        else:
            # 生成新的 run_id
            self.current_run_id = self._generate_run_id(workflow_name)
            logger.info(f"生成新的 run_id: {self.current_run_id}")
        
        # 重置阶段执行计数（新的运行）
        if not use_latest:
            self.phase_execution_count.clear()
        
        # 执行工作流
        result = self.execute_phases(
            phases=workflow["phases"],
            requirement=requirement,
            project_path=project_path,
            dry_run=dry_run,
            workflow_name=workflow_name,
            **kwargs
        )
        
        # 添加 run_id 到结果
        result["run_id"] = self.current_run_id
        
        return result
    
    def execute_phases(
        self,
        phases: List[Phase],
        requirement: str,
        project_path: str = None,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行阶段列表
        
        Args:
            phases: 阶段列表
            requirement: 原始需求
            project_path: 项目路径（dry_run 模式可选）
            dry_run: 是否为干运行模式
        
        Returns:
            执行结果
        """
        results = {
            "workflow": kwargs.get("workflow_name", "custom"),
            "success": True,
            "phases": [],
            "total_duration": 0,
            "total_iterations": 0,
            "status": "completed"
        }
        
        context = {
            "original_requirement": requirement
        }
        
        # 初始化工作区和访问策略
        if project_path and not dry_run:
            self.workspace = Workspace(project_path, self.current_run_id)
            self.workspace.ensure_directories()
            self.access_policy = AccessPolicy(self.workspace)
            logger.info(f"工作区已初始化: {self.workspace.workspace_root}")
            if self.current_run_id:
                logger.info(f"运行目录: {self.workspace.run_root}")
        
        start_time = time.time()
        
        logger.info("="*60)
        logger.info(f"开始工作流执行 {'(干运行模式)' if dry_run else ''}")
        logger.info(f"Run ID: {self.current_run_id}")
        logger.info(f"工作流: {kwargs.get('workflow_name', 'custom')}")
        logger.info(f"需求: {requirement[:80]}...")
        if project_path:
            logger.info(f"项目路径: {project_path}")
        logger.info(f"阶段数: {len(phases)}")
        logger.info("="*60)
        
        # 顺序执行每个阶段
        for i, phase in enumerate(phases, 1):
            # 跟踪阶段执行次数
            if phase.name not in self.phase_execution_count:
                self.phase_execution_count[phase.name] = 0
            self.phase_execution_count[phase.name] += 1
            iteration = self.phase_execution_count[phase.name]
            
            logger.info("="*60)
            logger.info(f"阶段 {i}/{len(phases)}: {phase.name} (第 {iteration} 次执行)")
            logger.info(f"Agent: {phase.agent}")
            logger.info(f"描述: {phase.description}")
            logger.info("="*60)
            
            if dry_run:
                # 干运行模式：只验证配置，不实际执行
                phase_result = self._dry_run_phase(phase, context)
            else:
                # 实际执行阶段
                if not self.client:
                    raise ValueError("需要 ClaudeCodeClient 才能执行工作流")
                if not project_path:
                    raise ValueError("需要 project_path 才能执行工作流")
                    
                phase_result = self._execute_phase(
                    phase=phase,
                    context=context,
                    project_path=project_path,
                    iteration=iteration
                )
            
            # 添加阶段信息到结果
            phase_result["phase"] = phase.name
            phase_result["agent"] = phase.agent
            
            # 保存阶段结果
            results["phases"].append(phase_result)
            results["total_iterations"] += phase_result.get("iterations", 0)
            
            # 检查阶段是否成功
            if not phase_result.get("success", False):
                results["success"] = False
                results["failed_phase"] = phase.name
                results["error"] = phase_result.get("error", "未知错误")
                results["status"] = "failed"
                
                logger.error(f"阶段失败: {phase.name}")
                logger.error(f"错误: {results['error']}")
                break
            
            # 保存阶段输出到文件
            output_file_path = None
            if not dry_run and phase.output_file and project_path:
                output_file_path = self._save_phase_output(
                    project_path,
                    phase.name,
                    phase.output_file,
                    phase_result.get("final_output", ""),
                    iteration
                )
            
            # 更新上下文（供下一阶段使用）
            # 使用文件路径而不是直接传递内容
            if output_file_path:
                context["previous_output_file"] = str(output_file_path)
                context["previous_output"] = f"请查看文件: {output_file_path}"
            else:
                context["previous_output"] = phase_result.get("final_output", "")
            
            context["phase_name"] = phase.name
            
            logger.info(f"阶段完成: {phase.name}")
            logger.info(f"轮数: {phase_result.get('iterations', 0)}, 耗时: {phase_result.get('duration', 0):.1f}秒, 状态: {phase_result.get('final_status', 'unknown')}")
            
            # 打印输出内容预览
            output = phase_result.get('final_output', '')
            logger.info(f"... (共 {len(output)} 字符)")
            logger.info(output)
                    
        
        results["total_duration"] = time.time() - start_time
        
        logger.info("="*60)
        if results["success"]:
            logger.info("工作流完成！")
        else:
            logger.error(f"工作流失败于阶段: {results.get('failed_phase')}")
        logger.info(f"总轮数: {results['total_iterations']}, 总耗时: {results['total_duration']:.1f}秒")
        logger.info("="*60)
        
        return results
    
    def _execute_phase(
        self,
        phase: Phase,
        context: Dict[str, Any],
        project_path: str,
        iteration: int = 1
    ) -> Dict[str, Any]:
        """执行单个阶段"""
        
        logger.debug(f"执行阶段: {phase.name}, Agent: {phase.agent}, 迭代: {iteration}")
        
        # 获取 Agent 信息
        agent_data = self.agent_library.get_agent(phase.agent)
        agent_prompt = self.agent_library.get_agent_prompt(phase.agent)
        
        if not agent_data or not agent_prompt:
            logger.error(f"Agent 不存在: {phase.agent}")
            return {
                "success": False,
                "error": f"Agent 不存在: {phase.agent}"
            }
        
        # 获取文件操作指导（基于 Agent 配置和工作区结构）
        file_guidance = self.access_policy.get_guidance(agent_data)
        
        # 格式化需求
        phase_requirement = phase.format_requirement(context)
        
        # 计算输出文件路径（用于告知 AI）
        if self.current_run_id:
            output_dir = f".claude/runs/{self.current_run_id}"
        else:
            output_dir = ".claude/runs/default"
        
        # 构建完整提示：任务在前，角色定义在后
        full_requirement = f"""
# 当前任务

{phase_requirement}

---

# 文件操作权限

{file_guidance}

**工作目录说明**：
- 主输出会自动保存到: {output_dir}/phases/{phase.output_file if phase.output_file else phase.name + '.md'}
- 你可以创建额外的文档和图表到指定目录
- 临时文件可以保存到: {output_dir}/temp/{phase.name}/

---

# 角色定义和参考资料

{agent_prompt}
"""
        
        # 执行多轮对话
        result = self.client.execute_multi_round_task(
            requirement=full_requirement,
            project_path=project_path
        )
        
        return result
    
    def _dry_run_phase(
        self,
        phase: Phase,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """干运行阶段（不实际执行）"""
        
        # 验证 Agent 存在
        agent_prompt = self.agent_library.get_agent_prompt(phase.agent)
        
        if not agent_prompt:
            return {
                "phase": phase.name,
                "agent": phase.agent,
                "success": False,
                "status": "failed",
                "error": f"Agent 不存在: {phase.agent}",
                "iterations": 0,
                "duration": 0
            }
        
        # 格式化需求（验证模板）
        try:
            phase_requirement = phase.format_requirement(context)
        except Exception as e:
            return {
                "phase": phase.name,
                "agent": phase.agent,
                "success": False,
                "status": "failed",
                "error": f"需求模板格式化失败: {e}",
                "iterations": 0,
                "duration": 0
            }
        
        # 返回模拟结果
        return {
            "phase": phase.name,
            "agent": phase.agent,
            "success": True,
            "status": "completed",
            "iterations": 1,
            "duration": 0.1,
            "final_output": f"[干运行] {phase.name} 阶段配置正确",
            "output_file": phase.output_file
        }
    
    def _save_phase_output(
        self,
        project_path: str,
        phase_name: str,
        output_file: str,
        content: str,
        iteration: int = 1
    ) -> Path:
        """
        保存阶段输出（支持迭代隔离和运行隔离）
        
        Args:
            project_path: 项目路径
            phase_name: 阶段名称
            output_file: 输出文件名
            content: 输出内容
            iteration: 迭代次数
        
        Returns:
            输出文件的绝对路径
        """
        # 使用工作区管理器获取输出路径
        output_path = self.workspace.get_phase_output_path(phase_name, output_file, iteration)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        
        # 返回绝对路径
        absolute_path = output_path.resolve()
        logger.info(f"保存阶段输出: {absolute_path}")
        
        return absolute_path
    
    def _load_workflow(self, workflow_name: str) -> Optional[Dict]:
        """加载工作流定义"""
        workflow_file = Path(__file__).parent / "workflows" / f"{workflow_name}.yaml"
        
        if not workflow_file.exists():
            logger.warning(f"工作流文件不存在: {workflow_file}")
            return None
        
        logger.debug(f"加载工作流: {workflow_name}")
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            # 转换为 Phase 对象
            phases = []
            for phase_data in workflow_data.get("phases", []):
                phase = Phase(
                    name=phase_data["name"],
                    agent=phase_data["agent"],
                    description=phase_data["description"],
                    requirement=phase_data["requirement"],
                    model=phase_data.get("model"),
                    max_iterations=phase_data.get("max_iterations", 10),
                    timeout=phase_data.get("timeout", 300),
                    output_file=phase_data.get("output_file"),
                    depends_on=phase_data.get("depends_on")
                )
                phases.append(phase)
            
            return {
                "name": workflow_data.get("name", workflow_name),
                "description": workflow_data.get("description", ""),
                "phases": phases
            }
            
        except Exception as e:
            logger.error(f"加载工作流失败 {workflow_name}: {e}", exc_info=True)
            return None
    
    def create_custom_workflow(
        self,
        phases: List[Dict[str, Any]]
    ) -> List[Phase]:
        """
        创建自定义工作流
        
        Args:
            phases: 阶段定义列表
        
        Returns:
            Phase 对象列表
        """
        phase_objects = []
        
        for phase_data in phases:
            phase = Phase(
                name=phase_data["name"],
                agent=phase_data["agent"],
                description=phase_data.get("description", ""),
                requirement=phase_data["requirement"],
                model=phase_data.get("model"),
                max_iterations=phase_data.get("max_iterations", 10),
                timeout=phase_data.get("timeout", 300),
                output_file=phase_data.get("output_file"),
                depends_on=phase_data.get("depends_on")
            )
            phase_objects.append(phase)
        
        return phase_objects
    
    def list_workflows(self) -> List[str]:
        """列出所有可用的工作流"""
        workflows_dir = Path(__file__).parent / "workflows"
        
        if not workflows_dir.exists():
            return []
        
        workflows = []
        for workflow_file in workflows_dir.glob("*.yaml"):
            workflows.append(workflow_file.stem)
        
        return sorted(workflows)
    
    def load_workflow(self, workflow_name: str) -> Optional[Dict]:
        """
        加载工作流定义（用于检查）
        
        Args:
            workflow_name: 工作流名称
        
        Returns:
            工作流定义字典
        """
        return self._load_workflow(workflow_name)
    
    def _generate_run_id(self, workflow_name: str) -> str:
        """
        生成运行ID
        
        格式：{workflow_name}_{timestamp}
        例如：standard_20240218_143052
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{workflow_name}_{timestamp}"
    
    def _get_latest_run_id(self, project_path: str, workflow_name: str) -> Optional[str]:
        """
        获取最新的运行ID
        
        Args:
            project_path: 项目路径
            workflow_name: 工作流名称
        
        Returns:
            最新的 run_id，如果没有则返回 None
        """
        runs_dir = Path(project_path) / ".claude" / "runs"
        
        if not runs_dir.exists():
            return None
        
        # 查找所有匹配的运行目录
        matching_runs = []
        for run_dir in runs_dir.iterdir():
            if run_dir.is_dir() and run_dir.name.startswith(f"{workflow_name}_"):
                matching_runs.append(run_dir.name)
        
        if not matching_runs:
            return None
        
        # 返回最新的（按名称排序，因为包含时间戳）
        return sorted(matching_runs)[-1]
    
    def list_runs(self, project_path: str, workflow_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有运行记录
        
        Args:
            project_path: 项目路径
            workflow_name: 工作流名称（可选，用于过滤）
        
        Returns:
            运行记录列表
        """
        runs_dir = Path(project_path) / ".claude" / "runs"
        
        if not runs_dir.exists():
            return []
        
        runs = []
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            
            # 过滤工作流名称
            if workflow_name and not run_dir.name.startswith(f"{workflow_name}_"):
                continue
            
            # 获取运行信息
            run_info = {
                "run_id": run_dir.name,
                "workflow": run_dir.name.split("_")[0],
                "timestamp": "_".join(run_dir.name.split("_")[1:]),
                "path": str(run_dir),
                "phases": []
            }
            
            # 列出阶段输出
            phases_dir = run_dir / "phases"
            if phases_dir.exists():
                for phase_file in phases_dir.glob("*.md"):
                    run_info["phases"].append(phase_file.stem)
            
            runs.append(run_info)
        
        # 按时间戳排序（最新的在前）
        return sorted(runs, key=lambda x: x["timestamp"], reverse=True)
    
    def get_run_output(self, project_path: str, run_id: str, phase_name: str) -> Optional[str]:
        """
        获取指定运行的阶段输出
        
        Args:
            project_path: 项目路径
            run_id: 运行ID
            phase_name: 阶段名称
        
        Returns:
            阶段输出内容，如果不存在则返回 None
        """
        output_file = Path(project_path) / ".claude" / "runs" / run_id / "phases" / f"{phase_name}.md"
        
        if not output_file.exists():
            return None
        
        return output_file.read_text(encoding='utf-8')

