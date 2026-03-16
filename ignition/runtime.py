"""
Resolve container runtime (docker or podman) from inventory defaults and env.
"""
from __future__ import annotations

import os
from typing import Any


def resolve_runtime(inventory: dict[str, Any] | None = None) -> str:
    """Returns 'docker' or 'podman'."""
    runtime = None
    if inventory:
        defaults = inventory.get("defaults") or {}
        if isinstance(defaults, dict):
            runtime = defaults.get("runtime")
    if not runtime:
        runtime = os.environ.get("DOCKER_OR_PODMAN")
    if not runtime:
        runtime = "podman"
    runtime = str(runtime).strip().lower()
    if runtime not in ("docker", "podman"):
        runtime = "podman"
    return runtime
