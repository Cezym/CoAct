"""Factory that creates CrewAI embedders configs from a YAML config."""

from pathlib import Path
from typing import Dict

from config_loader import load_yaml

CONFIG_PATH = Path(__file__).parent / "crew" / "config" / "embedders.yaml"


def build_embedders() -> Dict[str, Dict]:
    """Return a dict mapping model names to CrewAI embedders instances."""
    raw_cfg = load_yaml(CONFIG_PATH)
    embedders: Dict[str, Dict] = {}
    for name, cfg in raw_cfg.items():
        # The config must contain all keys required by crewai.Embedder
        embedders[name] = cfg
    return embedders


EMBEDDERS: Dict[str, Dict] = build_embedders()
