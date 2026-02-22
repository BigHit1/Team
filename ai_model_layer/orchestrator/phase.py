"""
Phase 定义
表示工作流中的一个阶段

yaml层与flow层的中间层，替换一些宏定义
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Phase:
    """工作流阶段"""
    
    name: str                    # 阶段名称
    agent: str                   # 使用的 Agent
    description: str             # 阶段描述
    requirement: str             # 任务需求（可以使用模板变量）
    
    # 可选配置
    model: Optional[str] = None  # 覆盖 Agent 的默认模型
    max_iterations: int = 10     # 最大迭代次数
    timeout: int = 300           # 超时时间（秒）
    
    # 输出配置
    output_file: Optional[str] = None  # 保存输出到文件
    
    # 依赖配置
    depends_on: Optional[str] = None   # 依赖的前一个阶段
    
    def format_requirement(self, context: Dict[str, Any]) -> str:
        """
        格式化需求（替换模板变量）
        
        支持的变量：
        - {previous_output}: 上一阶段的输出（简短提示或文件路径）
        - {previous_output_file}: 上一阶段输出文件的绝对路径
        - {phase_name}: 上一阶段的名称
        - {original_requirement}: 原始需求
        """
        requirement = self.requirement
        
        # 替换变量
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in requirement:
                requirement = requirement.replace(placeholder, str(value))
        
        return requirement

