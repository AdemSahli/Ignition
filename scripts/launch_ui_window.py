#!/usr/bin/env python3
"""
Launch Ignition UI in a desktop window (PyWebView).
Starts the FastAPI server in a background thread and opens the UI in a native window.
Requires: pip install pywebview
Run from repo root or pass --repo-root. Example:
  python scripts/launch_ui_window.py
  python scripts/launch_ui_window.py --repo-root C:\\path\\to\\artifacts --port 9080
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

# Add repo root so ignition is importable when run from scripts/
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _run_server(repo_root: Path, port: int, host: str = "127.0.0.1") -> None:
    import uvicorn
    from ignition import server as server_mod
    server_mod._repo_root = repo_root
    uvicorn.run(server_mod.app, host=host, port=port)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ignition UI in a desktop window")
    parser.add_argument("--repo-root", type=str, default=None,
                        help="Ignition repo root (default: parent of scripts/)")
    parser.add_argument("--port", type=int, default=9080,
                        help="Port for the UI server")
    parser.add_argument("--host", type=str,
                        default="127.0.0.1", help="Host to bind")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or os.environ.get(
        "IGNITION_REPO") or _REPO_ROOT).resolve()
    if not repo_root.is_dir():
        print(f"Repo root is not a directory: {repo_root}", file=sys.stderr)
        return 1

    try:
        import webview
    except ImportError:
        print("PyWebView is required. Install with: pip install pywebview",
              file=sys.stderr)
        return 1

    port = args.port
    host = args.host
    url = f"http://{host}:{port}/"

    server_thread = threading.Thread(
        target=_run_server,
        kwargs={"repo_root": repo_root, "port": port, "host": host},
        daemon=True,
    )
    server_thread.start()

    time.sleep(1.2)

    webview.create_window("Ignition", url, width=1200, height=800)
    webview.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
