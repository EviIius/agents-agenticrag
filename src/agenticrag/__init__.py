"""Local-first agent and agentic RAG experimentation workbench."""

from .agent import AgentConfig, BoundedAgenticRAGWorkflow
from .agent_tools import ToolBudget
from .domain import RAGResult
from .skills import SkillRegistry
from .supervisor import SupervisorAgentWorkflow, SupervisorConfig

__all__ = [
    "AgentConfig",
    "BoundedAgenticRAGWorkflow",
    "RAGResult",
    "SkillRegistry",
    "SupervisorAgentWorkflow",
    "SupervisorConfig",
    "ToolBudget",
]
__version__ = "0.4.0"
