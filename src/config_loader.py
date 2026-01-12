"""Utility for loading YAML configuration files."""

import yaml
from pathlib import Path
from typing import Any, Dict


def load_yaml(file_path: str | Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents as a dict.

    Parameters
    ----------
    file_path : str or Path
        Absolute or relative path to the YAML file.

    Returns
    -------
    dict
        Parsed YAML content.
    """
    p = Path(file_path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Configuration file not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
