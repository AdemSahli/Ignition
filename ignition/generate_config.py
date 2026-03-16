"""
Run Ansible playbook for config generation.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PLAYBOOK_REL = "ansible/playbooks/generate-config.yml"
INVENTORY_REL = "inventory.yaml"


def run_generate_config(repo_root: Path | str) -> None:
    repo_root = Path(repo_root).resolve()
    playbook = repo_root / "ansible" / "playbooks" / "generate-config.yml"
    inv_file = repo_root / INVENTORY_REL
    if not playbook.is_file():
        print(
            f"Warning: Ansible playbook not found: {playbook}", file=sys.stderr)
        return
    if sys.platform == "win32":
        _run_windows(repo_root, playbook, inv_file)
    else:
        _run_native(repo_root, playbook, inv_file)


def _run_windows(repo_root: Path, playbook: Path, inv_file: Path) -> None:
    wsl_exe = shutil.which("wsl")
    if wsl_exe:
        result = subprocess.run(
            [wsl_exe, "-e", "wslpath", "-a", str(repo_root)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            print("WSL path conversion failed.", file=sys.stderr)
            sys.exit(1)
        wsl_path = result.stdout.strip()
        check = subprocess.run(
            [wsl_exe, "bash", "-c", "command -v ansible-playbook"],
            capture_output=True, text=True, check=False,
        )
        if check.returncode != 0 or not check.stdout.strip():
            print(
                "Ansible not found in WSL. Install: sudo apt install ansible", file=sys.stderr)
            sys.exit(1)
        cmd = f"cd '{wsl_path}' && ansible-playbook ansible/playbooks/generate-config.yml -i inventory.yaml -e \"repo_root={wsl_path}\""
        result = subprocess.run(
            [wsl_exe, "-e", "bash", "-c", cmd], cwd=str(repo_root))
        if result.returncode != 0:
            sys.exit(result.returncode)
        return
    exe = shutil.which("ansible-playbook")
    if not exe:
        print("WSL required for Generate-Config on Windows or install Ansible.", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([exe, str(playbook), "-i", str(inv_file),
                            "-e", f"repo_root={str(repo_root)}"], cwd=str(repo_root))
    exe = shutil.which("ansible-playbook")
    if not exe:
        print("ansible-playbook not found. Install Ansible.", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([exe, str(playbook), "-i", str(inv_file),
                            "-e", f"repo_root={str(repo_root)}"], cwd=str(repo_root))
