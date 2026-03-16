"""
Status command: print table and optional JSON status map.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import compose
from . import modules
from . import runtime as runtime_mod

ID_W, NAME_W, TYPE_W, EN_W, DETAIL_W = 24, 26, 20, 10, 44


def trunc(s: str | None, w: int) -> str:
    if not s:
        return ""
    s = str(s)
    return s if len(s) <= w else s[: w - 3] + "..."


def run_status(inventory: dict[str, Any], component_id: str | None) -> None:
    components = inventory.get("components") or []
    if component_id:
        components = [c for c in components if isinstance(c, dict) and c.get("id") == component_id]
    fmt = f"{{0:<{ID_W}}} {{1:<{NAME_W}}} {{2:<{TYPE_W}}} {{3:<{EN_W}}} {{4:<{DETAIL_W}}}"
    print(fmt.format("Id", "Name", "Type", "Enabled", "Detail"))
    for c in components:
        if not isinstance(c, dict):
            continue
        enabled = "disabled" if c.get("enabled") is False else "enabled"
        ctype = c.get("type") or ""
        detail = f"compose: {c.get('composeFile', '')}" if c.get("composeFile") and not ctype.startswith("module.") else (f"path: {c.get('path', '')}" if ctype.startswith("module.") else "")
        print(fmt.format(trunc(c.get("id"), ID_W), trunc(c.get("name"), NAME_W), trunc(ctype, TYPE_W), enabled, trunc(detail, DETAIL_W)))


def get_status_map(inventory: dict[str, Any], repo_root: Path) -> dict[str, str]:
    components = inventory.get("components") or []
    repo_root = Path(repo_root)
    inv_defaults = inventory.get("defaults") or {}
    default_runtime = (inv_defaults.get("runtime") if isinstance(inv_defaults, dict) else None) or runtime_mod.resolve_runtime(inventory)
    status_by_path: dict[Path, str] = {}
    result: dict[str, str] = {}
    for c in components:
        if not isinstance(c, dict):
            continue
        cid = c.get("id")
        if not cid:
            continue
        ctype = (c.get("type") or "").strip()
        if ctype.startswith("module."):
            result[cid] = "running" if modules.is_module_running(repo_root, cid) else "stopped"
            continue
        compose_file = c.get("composeFile")
        if not compose_file:
            result[cid] = "n/a"
            continue
        path = Path(compose_file) if Path(compose_file).is_absolute() else repo_root / compose_file
        path = path.resolve()
        if path not in status_by_path:
            rt = (c.get("runtime") or default_runtime).strip().lower()
            if rt not in ("docker", "podman"):
                rt = "podman"
            status_by_path[path] = compose.compose_status(path, rt)
        result[cid] = status_by_path[path]
    return result
