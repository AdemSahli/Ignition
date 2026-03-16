# Smoke-test result

**Last updated:** After Python UI server and cleanup.

## CLI

- **control.ps1** delegates to `python -m ignition.cli`. Status, Up, Down, Generate-Config work as documented.
- **Status:** Pass with inventory at repo root (YAML or JSON; PyYAML required for YAML).
- **Up/Down (compose):** Require Docker or Podman; fail with a clear error if runtime is not available.
- **Generate-Config:** Requires WSL + Ansible on Windows; native Ansible on macOS/Linux.

## UI (Python server)

- **Start-IgnitionUI.ps1** launches the Python FastAPI server (`ignition.server`). No PowerShell HTTP logic.
- **Automated smoke test:** `.\scripts\smoke-test-ui.ps1` starts the server, calls `GET /api/components`, `GET /api/status`, and `POST /api/command` (Status), then stops the server. Expect **PASS** when dependencies and inventory are in place.
- **Manual:** Open http://localhost:9080/ after starting the server; table shows components and status; log sidebar shows command output.

## Cleanup applied

- **Removed:** `Invoke-Compose.ps1`, `Get-Runtime.ps1`, `Invoke-ModuleProcess.ps1` — unused (Python `ignition.compose`, `ignition.runtime`, and `ignition.modules` implement the behaviour).
- **Docs:** Ignition-repo-layout.md, scripts/README.md, compose/README.md, and test-checklist.md updated for Python-based CLI and UI.
