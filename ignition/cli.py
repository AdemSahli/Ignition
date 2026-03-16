"""
Ignition CLI: status, up, down, generate-config.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import compose
from . import generate_config
from . import inventory
from . import modules
from . import runtime
from . import status_cmd


def _repo_root(s: str) -> Path:
    p = Path(s).resolve()
    if not p.is_dir():
        raise argparse.ArgumentTypeError(f"Repo root does not exist or is not a directory: {s}")
    return p


def main() -> None:
    parser = argparse.ArgumentParser(description="Ignition CLI: Status, Up, Down, Generate-Config")
    parser.add_argument("--repo-root", type=_repo_root, default=None, help="Ignition repo root (default: cwd or IGNITION_REPO)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    sp_status = subparsers.add_parser("status", help="List components")
    sp_status.add_argument("--component-id", type=str, default=None)
    sp_status.add_argument("--output", type=str, choices=("table", "json"), default="table")
    sp_up = subparsers.add_parser("up", help="Start compose and module processes")
    sp_up.add_argument("--component-id", type=str, action="append", dest="component_ids", default=None)
    sp_up.add_argument("--all", action="store_true")
    sp_up.add_argument("--show-module-console", action="store_true")
    sp_up.add_argument("--log-module-to-file", action="store_true")
    sp_down = subparsers.add_parser("down", help="Stop compose and module processes")
    sp_down.add_argument("--component-id", type=str, action="append", dest="component_ids", default=None)
    sp_down.add_argument("--all", action="store_true")
    subparsers.add_parser("generate-config", help="Run Ansible to generate config")

    args = parser.parse_args()
    repo_root = args.repo_root
    if repo_root is None:
        repo_root = Path.cwd()
        if "IGNITION_REPO" in __import__("os").environ:
            repo_root = Path(__import__("os").environ["IGNITION_REPO"]).resolve()
    if not repo_root.is_dir():
        print(f"Repo root is not a directory: {repo_root}", file=sys.stderr)
        sys.exit(1)

    inv_data: dict | None = None
    if args.command != "generate-config":
        try:
            inv_data = inventory.load_inventory(repo_root)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Failed to load inventory: {e}", file=sys.stderr)
            sys.exit(1)

    if args.command == "status":
        if getattr(args, "output", "table") == "json":
            print(json.dumps({"status": status_cmd.get_status_map(inv_data, repo_root)}))
        else:
            status_cmd.run_status(inv_data, getattr(args, "component_id", None))
        return
    if args.command == "up":
        ids = getattr(args, "component_ids", None) or []
        if getattr(args, "all", False) or not ids:
            ids = []
        rt = runtime.resolve_runtime(inv_data)
        compose.run_compose_up_down(inv_data, repo_root, ids if ids else None, rt, "up")
        modules.start_modules(inv_data, repo_root, ids if ids else None,
            show_console=getattr(args, "show_module_console", False),
            log_to_file=getattr(args, "log_module_to_file", False))
        return
    if args.command == "down":
        ids = getattr(args, "component_ids", None) or []
        if getattr(args, "all", False) or not ids:
            ids = []
        rt = runtime.resolve_runtime(inv_data)
        compose.run_compose_up_down(inv_data, repo_root, ids if ids else None, rt, "down")
        modules.stop_modules(inv_data, repo_root, ids if ids else None)
        return
    if args.command == "generate-config":
        generate_config.run_generate_config(repo_root)
        return
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
