"""Loading of the YAML configuration files."""
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Union

import yaml

CONFIG_ENV_VAR = "TOFAWIKI_CONFIG"

# Used when the service is run from a checkout without an explicit config path.
REPO_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def deep_merge(base: Mapping[str, Any], other: Mapping[str, Any]) -> Dict[str, Any]:
    """Merge ``other`` into ``base`` recursively, without mutating either."""
    merged = dict(base)
    for key, value in other.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def load_files(paths: Iterable[Union[str, Path]]) -> Dict[str, Any]:
    """Load YAML documents and merge them, later files winning."""
    config: Dict[str, Any] = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            document = yaml.safe_load(f) or {}
        if not isinstance(document, Mapping):
            raise ValueError(f"{path} does not contain a YAML mapping")
        config = deep_merge(config, document)
    return config


def find_config_dir(directory: Optional[Union[str, Path]] = None) -> Path:
    """Resolve the directory holding the ``*.yaml`` config files.

    The first of these that exists wins: the explicit argument, the
    ``TOFAWIKI_CONFIG`` environment variable, ``config/`` relative to the
    working directory, and ``config/`` next to the package.
    """
    candidates = [directory, os.environ.get(CONFIG_ENV_VAR), Path("config"), REPO_CONFIG_DIR]
    for candidate in candidates:
        if candidate and Path(candidate).is_dir():
            return Path(candidate)

    explicit = directory or os.environ.get(CONFIG_ENV_VAR)
    if explicit:
        raise FileNotFoundError(f"Config directory {explicit} does not exist")
    raise FileNotFoundError(
        f"Could not find a config directory. Pass one explicitly or set ${CONFIG_ENV_VAR}."
    )


def load_config(directory: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load and merge every ``*.yaml`` file in the config directory."""
    config_dir = find_config_dir(directory)
    paths = sorted(config_dir.glob("*.yaml"))
    if not paths:
        raise FileNotFoundError(f"No *.yaml config files found in {config_dir}")
    return load_files(paths)
