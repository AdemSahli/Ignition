"""
Start/stop module processes (module.springboot, module.angular).
Cross-OS: Windows uses cmd.exe; Unix uses subprocess with cwd and shell.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

RUN_DIR = ".ignition/run"


def _default_command(ctype: str) -> str:
    if ctype == "module.springboot":
        return "mvn spring-boot:run"
    if ctype == "module.angular":
        return "ng serve"
    return "true"


def get_module_components(
    inventory: dict[str, Any], component_ids: list[str] | None
) -> list[dict[str, Any]]:
    """Return enabled components with type module.* and a path. Filter by component_ids if set."""
    components = inventory.get("components") or []
    out = []
    for c in components:
        if not isinstance(c, dict):
            continue
        if c.get("enabled") is False:
            continue
        ctype = c.get("type") or ""
        if not ctype.startswith("module."):
            continue
        if not c.get("path"):
            continue
        if component_ids and c.get("id") not in component_ids:
            continue
        out.append(c)
    return out


def run_dir(repo_root: Path) -> Path:
    return Path(repo_root) / RUN_DIR.replace("/", os.sep)


def is_module_running(repo_root: Path, component_id: str) -> bool:
    """Return True if the module has a PID file and that process is still alive."""
    repo_root = Path(repo_root)
    pid_file = run_dir(repo_root) / f"{component_id}.pid"
    if not pid_file.is_file():
        return False
    try:
        pid_val = pid_file.read_text(encoding="utf-8").strip()
        pid = int(pid_val)
    except (ValueError, OSError):
        return False
    return _process_exists(pid)


def start_modules(
    inventory: dict[str, Any],
    repo_root: Path,
    component_ids: list[str] | None,
    show_console: bool = False,
    log_to_file: bool = False,
) -> None:
    """Start each module process; write PID to .ignition/run/<id>.pid. Optional log to .log."""
    repo_root = Path(repo_root)
    rdir = run_dir(repo_root)
    rdir.mkdir(parents=True, exist_ok=True)
    components = get_module_components(inventory, component_ids)
    for c in components:
        path_s = (c.get("path") or "").strip()
        if not path_s:
            continue
        path = Path(path_s)
        if not path.is_absolute():
            path = (repo_root / path).resolve()
        if not path.is_dir():
            print(f"Warning: Module path not found: {path} (component: {c.get('id')})", file=sys.stderr)
            continue
        ctype = c.get("type") or ""
        command = c.get("command") or _default_command(ctype)
        args_list = c.get("args") or []
        if ctype == "module.springboot" and c.get("profile"):
            args_list = list(args_list) + [f"-Dspring.profiles.active={c['profile']}"]
        args_str = " ".join(str(a) for a in args_list)
        full_command = f"{command} {args_str}".strip() if args_str else command
        cid = c.get("id") or "unknown"
        name = c.get("name") or cid
        print(f"Start module: {name} ({cid}) at {path}")
        pid_file = rdir / f"{cid}.pid"
        log_file = rdir / f"{cid}.log" if log_to_file else None
        if log_to_file:
            print(f"  Logs: {log_file}")
        _start_one(
            cwd=path,
            full_command=full_command,
            pid_file=pid_file,
            log_file=log_file,
            show_console=show_console,
        )


def _start_one(
    cwd: Path,
    full_command: str,
    pid_file: Path,
    log_file: Path | None,
    show_console: bool,
) -> None:
    is_windows = sys.platform == "win32"
    stdout_dest: int | None = subprocess.DEVNULL
    stderr_dest: int | None = subprocess.DEVNULL
    if log_file:
        log_handle = open(log_file, "w", encoding="utf-8")  # noqa: SIM115
        stdout_dest = log_handle
        stderr_dest = subprocess.STDOUT
    creationflags = 0
    if is_windows:
        if show_console:
            creationflags = subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    proc = subprocess.Popen(
        full_command,
        shell=True,
        cwd=str(cwd),
        stdout=stdout_dest,
        stderr=stderr_dest,
        start_new_session=not is_windows,
        creationflags=creationflags if is_windows else 0,
    )
    pid_file.write_text(str(proc.pid), encoding="utf-8")


def stop_modules(
    inventory: dict[str, Any],
    repo_root: Path,
    component_ids: list[str] | None,
) -> None:
    """Stop module processes by reading .ignition/run/*.pid and terminating."""
    repo_root = Path(repo_root)
    rdir = run_dir(repo_root)
    if not rdir.is_dir():
        return
    ids_to_stop = set(component_ids) if component_ids else None
    for pid_file in rdir.glob("*.pid"):
        cid = pid_file.stem
        if ids_to_stop and cid not in ids_to_stop:
            continue
        try:
            pid_val = pid_file.read_text(encoding="utf-8").strip()
            pid = int(pid_val)
        except (ValueError, OSError):
            pid_file.unlink(missing_ok=True)
            continue
        if _process_exists(pid):
            print(f"Stop module: {cid} (PID {pid})")
            _terminate_process(pid)
        else:
            print(f"Stop module: {cid} (PID {pid}) - process already ended, removing PID file")
        pid_file.unlink(missing_ok=True)


def _process_exists(pid: int) -> bool:
    """Return True if a process with the given PID exists. Cross-platform (Windows-safe)."""
    if sys.platform == "win32":
        return _process_exists_win(pid)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _process_exists_win(pid: int) -> bool:
    """Windows: use OpenProcess to check existence (os.kill(pid, 0) can raise WinError 87)."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False


def _terminate_process(pid: int) -> None:
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, check=False)
    else:
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            pass
