from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TaskStep:
    """Represents a single step in a structured TaskModel sequence."""
    step_number: int
    workspace: str
    action: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    is_completed: bool = False

@dataclass
class TaskModel:
    """Represents a complete, human-level structured task model built before execution."""
    raw_query: str
    primary_goal: str
    workspace: str
    target: str
    objects: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    sequence: List[TaskStep] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    completion_condition: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts TaskModel to dictionary format for logging and inspection."""
        return {
            "raw_query": self.raw_query,
            "primary_goal": self.primary_goal,
            "workspace": self.workspace,
            "target": self.target,
            "objects": self.objects,
            "parameters": self.parameters,
            "sequence": [
                {
                    "step": s.step_number,
                    "workspace": s.workspace,
                    "action": s.action,
                    "target": s.target,
                    "parameters": s.parameters,
                    "expected_result": s.expected_result
                } for s in self.sequence
            ],
            "dependencies": self.dependencies,
            "completion_condition": self.completion_condition
        }
