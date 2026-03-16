# Scripts (Ignition)

Run from the **Ignition repo root** (where `inventory.yaml`, `ignition/`, and `compose/` live), or set `$env:IGNITION_REPO` to that path. The CLI and UI server are implemented in Python (`ignition`); these scripts are launchers.

## Ignition.ps1

```powershell
# List all components
.\scripts\Ignition.ps1 -Command Status

# Start all (compose-based infra/monitoring + module processes in background)
.\scripts\Ignition.ps1 -Command Up

# Start one component by id
.\scripts\Ignition.ps1 -Command Up -ComponentId broker-activemq

# Stop all compose-based components
.\scripts\Ignition.ps1 -Command Down

# Stop one component
.\scripts\Ignition.ps1 -Command Down -ComponentId keycloak

# Generate application.yml and environment.ts (runs Ansible in WSL)
.\scripts\Ignition.ps1 -Command Generate-Config
```

**Inventory:** `inventory.yaml`, `inventory.yml`, or `inventory.json` at repo root. YAML requires PyYAML (pip install -r requirements.txt).

**Generate-Config:** Requires WSL and Ansible installed in the WSL distro; repo path is passed via `wslpath`.

## Start-IgnitionUI.ps1 (Windows) / start-ignition-ui.sh (macOS/Linux)

Launches the **Python UI server** (FastAPI) on http://localhost:9080 (default). **Windows:** `.\scripts\Start-IgnitionUI.ps1` with optional `-RepoRoot`, `-Port`. **macOS/Linux:** `./scripts/start-ignition-ui.sh` with optional `--repo-root`, `--port` (run `chmod +x scripts/start-ignition-ui.sh` once). The server serves `ui/index.html` and exposes `/api/components` (inventory), `/api/status` (runtime status), and `POST /api/command` (runs the ignition CLI). Alternative: run `python -m ignition.server --repo-root <path> --port 9080` from repo root. Optional desktop window: `pip install pywebview` then `python scripts/launch_ui_window.py`.
