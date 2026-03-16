"""
Load Ignition inventory from repo root (YAML or JSON).
Resolves path: inventory.yaml > inventory.yml > inventory.json.
Expands env vars in path strings for cross-OS (e.g. ${HOME}, %USERPROFILE%).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

INVENTORY_NAMES = ("inventory.yaml", "inventory.yml", "inventory.json")


def find_inventory_path(repo_root: Path) -> Path:
    """Return path to first existing inventory file under repo_root."""
    for name in INVENTORY_NAMES:
        p = repo_root / name
        if p.is_file():
            return p
    raise FileNotFoundError(
        f"No inventory file found under {repo_root} "
        "(inventory.yaml, inventory.yml, or inventory.json). "
        "Ensure repo root is correct."
    )


def load_inventory(repo_root: Path | str) -> dict[str, Any]:
    """Load inventory from repo root. Returns dict with 'defaults' and 'components'."""
    repo_root = Path(repo_root)
    path = find_inventory_path(repo_root)
    raw = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()
    if ext == ".json":
        data = json.loads(raw)
    elif ext in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError(
                "YAML inventory requires PyYAML. Install with: pip install pyyaml"
            )
        data = yaml.safe_load(raw)
    else:
        raise ValueError(f"Unsupported inventory format: {ext}")
    if not isinstance(data, dict):
        raise ValueError("Inventory root must be a dict (defaults, components).")
    for comp in data.get("components") or []:
        if isinstance(comp, dict) and "path" in comp and comp["path"]:
            comp["path"] = expand_path(comp["path"])
    return data


def expand_path(s: str) -> str:
    """Expand ${VAR}, $VAR (Unix), and %VAR% (Windows) using os.environ."""
    out = s
    for key, value in os.environ.items():
        if value is None:
            continue
        out = out.replace(f"${{{key}}}", value)
        out = out.replace(f"%{key}%", value)
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        return os.environ.get(key, m.group(0))
    out = re.sub(r"\$([a-zA-Z_][a-zA-Z0-9_]*)", repl, out)
    return out
