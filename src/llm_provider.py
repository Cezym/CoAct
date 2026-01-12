"""Factory that creates CrewAI LLM instances from a YAML config."""

from pathlib import Path
from typing import Dict

from crewai import LLM

from config_loader import load_yaml

CONFIG_PATH = Path(__file__).parent / "crew" / "config" / "llm_providers.yaml"


def build_llms() -> Dict[str, LLM]:
    """Return a dict mapping model names to CrewAI LLM instances."""
    raw_cfg = load_yaml(CONFIG_PATH)
    llms: Dict[str, LLM] = {}
    for name, cfg in raw_cfg.items():
        # The config must contain all keys required by crewai.LLM
        llms[name] = LLM(**cfg)
    return llms


LLMS: Dict[str, LLM] = build_llms()
