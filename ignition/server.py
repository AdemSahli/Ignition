"""
Ignition UI server: FastAPI app for HTML/JS UI and API.
Run: python -m ignition.server --repo-root <path> [--port 9080]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.requests import Request

from . import inventory
from . import status_cmd

_repo_root: Path | None = None


def get_repo_root() -> Path:
    if _repo_root is None or not _repo_root.is_dir():
        raise HTTPException(status_code=503, detail="Repo root not configured or invalid.")
    return _repo_root


def _err_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


app = FastAPI(title="Ignition UI", description="Local UI for Ignition")


@app.get("/", response_class=HTMLResponse, response_model=None)
@app.get("/index.html", response_class=HTMLResponse, response_model=None)
def serve_index():
    repo_root = get_repo_root()
    path = repo_root / "ui" / "index.html"
    if not path.is_file():
        return _err_response(404, "UI not found")
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@app.get("/ignition.svg", response_class=FileResponse)
def serve_logo():
    repo_root = get_repo_root()
    path = repo_root / "ui" / "ignition.svg"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Logo not found")
    return FileResponse(path, media_type="image/svg+xml")


@app.get("/api/components")
def api_components() -> JSONResponse:
    repo_root = get_repo_root()
    try:
        inv = inventory.load_inventory(repo_root)
    except Exception as e:
        return _err_response(503, str(e))
    return JSONResponse(content=inv)


@app.get("/api/status")
def api_status() -> JSONResponse:
    repo_root = get_repo_root()
    try:
        inv = inventory.load_inventory(repo_root)
        status_map = status_cmd.get_status_map(inv, repo_root)
    except Exception as e:
        return _err_response(503, str(e))
    return JSONResponse(content={"status": status_map})


_COMMAND_MAP = {"up": "Up", "down": "Down", "up all": "Up", "down all": "Down", "generate-config": "Generate-Config", "status": "Status"}
VALID_COMMANDS = ("Up", "Down", "Generate-Config", "Status")


@app.post("/api/command")
async def api_command(request: Request) -> JSONResponse:
    repo_root = get_repo_root()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    raw = (body.get("command") or body.get("Command") or "").strip()
    command = _COMMAND_MAP.get(raw.lower(), raw) if raw else ""
    component_id = (body.get("componentId") or "").strip() or None
    if command not in VALID_COMMANDS:
        return _err_response(400, f"Invalid command. Allowed: {', '.join(VALID_COMMANDS)}.")
    cli_command = command.lower().replace(" ", "-")
    args = [sys.executable, "-m", "ignition.cli", "--repo-root", str(repo_root), cli_command]
    if command in ("Up", "Down") and not component_id:
        args.append("--all")
    elif component_id:
        args.extend(["--component-id", component_id])
    try:
        result = subprocess.run(args, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        out = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0:
            err_msg = out.strip() or f"Command failed with exit code {result.returncode}"
            return _err_response(502, err_msg)
        return JSONResponse(content={"output": out or "Done."})
    except subprocess.TimeoutExpired:
        return _err_response(504, "Command timed out")
    except Exception as e:
        return _err_response(500, str(e))


def run_server(repo_root: Path, port: int = 9080, host: str = "127.0.0.1") -> None:
    global _repo_root
    _repo_root = Path(repo_root).resolve()
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Ignition UI server")
    parser.add_argument("--repo-root", type=str, default=None, help="Ignition repo root")
    parser.add_argument("--port", type=int, default=9080)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
    repo_root = Path(args.repo_root or os.environ.get("IGNITION_REPO") or os.getcwd()).resolve()
    if not repo_root.is_dir():
        print(f"Repo root is not a directory: {repo_root}", file=sys.stderr)
        sys.exit(1)
    print(f"Ignition UI: http://{args.host}:{args.port}/ (RepoRoot: {repo_root}). Press Ctrl+C to stop.")
    run_server(repo_root, port=args.port, host=args.host)
