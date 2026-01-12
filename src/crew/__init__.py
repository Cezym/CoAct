"""
Shared logic for loading agents/tasks config.

Both DevelopersCrew and CodeEvaluationCrew import the mixin below.
"""

from pathlib import Path
from typing import Dict, Any

from config_loader import load_yaml


class CrewConfigMixin:
    """
    Mixin that supplies two properties:

        - crew_agents_config (Dict[str, Any])
        - crew_tasks_config  (Dict[str, Any])
    """

    CREW_PATH = Path(__file__).resolve().parent
    _agents_cfg_path: str = str(CREW_PATH / "config" / "agents.yaml")
    _tasks_cfg_path: str = str(CREW_PATH / "config" / "tasks.yaml")
    _embedders_cfg_path: str = str(CREW_PATH / "config" / "tasks.yaml")

    @staticmethod
    def crew_agents_config() -> Dict[str, Any]:
        """Return the agents YAML configuration."""
        return load_yaml(CrewConfigMixin._agents_cfg_path)

    @staticmethod
    def crew_tasks_config() -> Dict[str, Any]:
        """Return the tasks YAML configuration."""
        return load_yaml(CrewConfigMixin._tasks_cfg_path)


__all__ = ["CrewConfigMixin"]
