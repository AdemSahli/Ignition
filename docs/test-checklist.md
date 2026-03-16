# Ignition test checklist

Use this checklist to smoke-test the CLI and UI after setup or changes. See **runbooks.md** §0 for first-time setup.

---

## Quick test (automated)

From the **artifacts** folder (repo root):

```powershell
.\scripts\smoke-test-ui.ps1
```

This starts the Python UI server, hits `GET /api/components`, `GET /api/status`, and `POST /api/command` (Status), then stops the server. Expect **"UI smoke test: PASS"** if dependencies are installed and inventory exists.

---

## Prerequisites

Before running tests, ensure:

| Item                                   | Required for        | Notes                                                                                                                                         |
| -------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inventory** at repo root             | CLI, UI             | One of `inventory.yaml`, `inventory.yml`, or `inventory.json`. Copy from `inventory.example.yaml` and edit, or use `inventory.json` for JSON. |
| **YAML support** (if using .yaml/.yml) | CLI Status, UI      | `Install-Module powershell-yaml` or WSL + Python + PyYAML. Alternatively use `inventory.json` to avoid YAML.                                  |
| **Docker or Podman** + Compose         | Up / Down (compose) | Set `defaults.runtime` in inventory or `$env:DOCKER_OR_PODMAN`.                                                                               |
| **WSL + Ansible**                      | Generate-Config     | Only if you test config generation.                                                                                                           |

Repo root = directory that contains `inventory.*`, `compose/`, and `scripts/`. Use `-RepoRoot` or run from that directory (or set `$env:IGNITION_REPO`).

---

## CLI tests

Run from a PowerShell console. All commands assume repo root is current directory or pass `-RepoRoot C:\path\to\ignition`.

| Step                  | Command                                                       | Expected outcome                                                                                                                                                    |
| --------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Status             | `.\scripts\Ignition.ps1 -Command Status`                       | Exit 0. Table with columns Id, Name, Type, Enabled, Detail. All inventory components listed; compose components show `compose: <file>`, modules show `path: <dir>`. |
| 2. Status (one id)    | `.\scripts\Ignition.ps1 -Command Status -ComponentId keycloak` | Exit 0. Single row for that component.                                                                                                                              |
| 3. Up (one compose)   | `.\scripts\Ignition.ps1 -Command Up -ComponentId keycloak`     | If Docker/Podman is installed: exit 0, "Up: Keycloak ...", compose stack starts. If not installed: exit non-zero, clear error (e.g. "podman not recognized").       |
| 4. Down (one compose) | `.\scripts\Ignition.ps1 -Command Down -ComponentId keycloak`   | Exit 0, "Down: Keycloak ...", stack stopped.                                                                                                                        |
| 5. Generate-Config    | `.\scripts\Ignition.ps1 -Command Generate-Config`              | If WSL + Ansible: exit 0, Ansible runs, `generated/` contains output. If WSL missing: exit with message "WSL is required for Generate-Config".                      |

**Optional:** Up All, Down All (starts/stops all enabled compose components and then module processes). Down also stops module processes via `.ignition/run/<id>.pid`.

---

## UI tests

The UI is served by the **Python (FastAPI)** server. Start it from a console:

```powershell
.\scripts\Start-IgnitionUI.ps1 -RepoRoot C:\path\to\ignition
```

Or from repo root: `python -m ignition.server --repo-root . --port 9080`. Then open **http://localhost:9080/** in a browser. If port 9080 is in use, use `-Port 9081` (or `--port 9081`) and open the corresponding URL.

| Step                 | Action                                  | Expected outcome                                                                                |
| -------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1. Component list    | Open http://localhost:9080/             | Page loads. Table shows all components (id, name, type, status, detail).                        |
| 2. Status command    | Click **Status** (or use toolbar / API) | Log sidebar shows CLI Status output.                                                            |
| 3. Up All / Down All | Click **Up All** or **Down All**        | Same behaviour as CLI; log sidebar shows result. Requires Docker/Podman for compose components. |

**API checks (optional):**

- `GET http://localhost:9080/api/components` → 200, JSON with `defaults` and `components`.
- `GET http://localhost:9080/api/status` → 200, JSON with `status` (component id → running/stopped/n/a).
- `POST http://localhost:9080/api/command` with body `{"command":"Status"}` → 200, JSON with `output` containing Status text.

---

## Quick reference

- **CLI:** `Ignition.ps1 -Command Status|Up|Down|Generate-Config` with optional `-ComponentId`, `-RepoRoot`.
- **UI:** `Start-IgnitionUI.ps1 -RepoRoot <path>` or `python -m ignition.server --repo-root .` then browser at http://localhost:9080/.
- **Automated UI test:** `.\scripts\smoke-test-ui.ps1` (from repo root).
- **Docs:** Runbooks = **runbooks.md**; layout = **ignition-repo-layout.md**; smoke-test results = **smoke-test-result.md**.
