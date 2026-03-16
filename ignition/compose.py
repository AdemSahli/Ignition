"""
Run docker/podman compose up/down. One subprocess per unique compose file.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def compose_up(compose_file: Path, runtime: str) -> None:
    _compose_cmd(compose_file, runtime, ["up", "-d"])


def compose_down(compose_file: Path, runtime: str) -> None:
    _compose_cmd(compose_file, runtime, ["down"])


def _compose_cmd(compose_file: Path, runtime: str, args: list[str]) -> None:
    compose_file = Path(compose_file).resolve()
    if not compose_file.is_file():
        raise FileNotFoundError(f"Compose file not found: {compose_file}")
    runtime = runtime.strip().lower()
    if runtime not in ("docker", "podman"):
        runtime = "podman"
    exe = shutil.which(runtime)
    if not exe:
        raise RuntimeError(f"Runtime '{runtime}' not found on PATH.")
    full_args = [exe, "compose", "-f", str(compose_file)] + args
    result = subprocess.run(full_args, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)


def compose_status(compose_file: Path, runtime: str) -> str:
    compose_file = Path(compose_file).resolve()
    if not compose_file.is_file():
        return "unknown"
    runtime = runtime.strip().lower()
    if runtime not in ("docker", "podman"):
        runtime = "podman"
    exe = shutil.which(runtime)
    if not exe:
        return "unknown"
    full_args = [exe, "compose", "-f", str(compose_file), "ps", "-a", "--format", "json"]
    try:
        result = subprocess.run(full_args, capture_output=True, text=True, timeout=15, check=False)
    except (subprocess.TimeoutExpired, OSError):
        return "unknown"
    if result.returncode != 0:
        return "stopped"
    def has_running(obj: Any) -> bool:
        if isinstance(obj, dict):
            return (obj.get("State") or obj.get("state") or "").lower() == "running"
        if isinstance(obj, list):
            return any(has_running(x) for x in obj)
        return False
    for line in (result.stdout or "").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            if has_running(json.loads(line)):
                return "running"
        except json.JSONDecodeError:
            if "running" in line.lower():
                return "running"
    return "stopped"


def get_compose_components(
    inventory: dict[str, Any], component_ids: list[str] | None
) -> list[dict[str, Any]]:
    components = inventory.get("components") or []
    out = []
    for c in components:
        if not isinstance(c, dict) or c.get("enabled") is False or not c.get("composeFile"):
            continue
        if (c.get("type") or "").startswith("module."):
            continue
        if component_ids and c.get("id") not in component_ids:
            continue
        out.append(c)
    return out


def run_compose_up_down(
    inventory: dict[str, Any],
    repo_root: Path,
    component_ids: list[str] | None,
    runtime: str,
    action: str,
) -> None:
    components = get_compose_components(inventory, component_ids)
    inv_defaults = inventory.get("defaults") or {}
    default_runtime = (inv_defaults.get("runtime") if isinstance(inv_defaults, dict) else None) or runtime
    repo_root = Path(repo_root)
    seen: set[Path] = set()
    for c in components:
        compose_file = c.get("composeFile")
        if not compose_file:
            continue
        path = Path(compose_file) if Path(compose_file).is_absolute() else repo_root / compose_file
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            print(f"Warning: Compose file not found: {path} (component: {c.get('id')})", file=sys.stderr)
            continue
        rt = (c.get("runtime") or default_runtime).strip().lower()
        if rt not in ("docker", "podman"):
            rt = "podman"
        if action == "up":
            compose_up(path, rt)
        else:
            compose_down(path, rt)
