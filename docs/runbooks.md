# Ignition runbooks

How to add a module, switch broker, and use the CLI and UI.

---

## 0. First-time setup / prerequisites

Before using the CLI or UI, set up the Ignition repo and dependencies. **On a new computer, use [setup-and-troubleshooting.md](setup-and-troubleshooting.md) for the full checklist and common fixes.**

1. **Get the repo** — Clone or copy the Ignition repo to your machine. The repo root is where `inventory.yaml`, `compose/`, and `scripts/` live.

2. **Inventory** — Copy `inventory.example.yaml` to `inventory.yaml` (or `inventory.yml`) at the repo root. Edit it: set `defaults.runtime` (e.g. `podman` or `docker`), add or enable the components you need (broker, Elasticsearch, Keycloak, your modules), and set each module’s `path` to the actual directory (absolute path or `$env:APP_REPO\...`).

3. **YAML support** (for inventory) — Either:
   - **PowerShell:** `Install-Module powershell-yaml -Scope CurrentUser` (run from Windows PowerShell; no WSL needed), or
   - **WSL:** The CLI can use WSL to parse YAML if powershell-yaml is not installed. **You must run the CLI from Windows PowerShell** (not from inside a WSL terminal). In WSL (Debian/Ubuntu), install the system PyYAML package:
     ```bash
     sudo apt update && sudo apt install -y python3-yaml
     ```
     (If your distro has no `python3-yaml`, use a venv: `python3 -m venv ~/.venv-yaml && ~/.venv-yaml/bin/pip install pyyaml` and ensure `~/.venv-yaml/bin/python3` is on PATH when WSL runs, or use `pip3 install --user pyyaml` if your distro allows it.)
     From **Windows PowerShell** verify: `wsl python3 -c "import yaml; print('OK')"` (should print OK).

4. **Generate-Config** — Requires **WSL** with **Ansible** installed (`pip install ansible` or your distro’s package). The repo path must be reachable from WSL. In WSL install Ansible: `sudo apt install ansible` or `pip3 install --user ansible`.

5. **Runtime (Compose)** — Install **Docker** or **Podman** and ensure the Compose CLI is available (`docker compose` or `podman compose`). Set `defaults.runtime` in inventory or `$env:DOCKER_OR_PODMAN` to `docker` or `podman`.

6. **Optional:** Set `$env:IGNITION_REPO` to the Ignition repo root so you can run the CLI from any directory. Set `$env:APP_REPO` to your multi-module app root if you use it in module `path` values.

After this, run **Status** to confirm the inventory loads, then **Up** or **Up All** to start the stack.

---

## 1. How to add a module

Modules are Spring Boot (Java) or Angular apps that run as processes (not in containers). Adding one = adding an entry to the **inventory**; no code change in Ignition.

### 1.1 Add a Spring Boot module

1. Open **inventory.yaml** (or inventory.yml / inventory.json) at the Ignition repo root.
2. Under `components:`, add an entry:

```yaml
- id: service-myservice # unique id (used in CLI/UI)
  type: module.springboot
  name: My Service # human-readable label
  group: backend # optional; for grouping
  path: C:\dev\app\myservice # root dir of the module (or use $env:APP_REPO\myservice)
  port: 8082 # optional; for display
  command: mvn spring-boot:run # optional; default is mvn spring-boot:run
  profile: dev # optional; passed as -Dspring.profiles.active
  # args:                        # optional list, e.g. ["-Dserver.port=8082"]
```

3. Save. The module appears in **Status** and in the UI. **Up** or **Up All** will start it (after Compose-based components) as a background process.

**Path:** Use an **absolute** path to the module directory, or a path relative to the **Ignition repo root** (rare for app modules—that would put the module under the Ignition repo). If your app lives in a separate repo, prefer an absolute path or `$env:APP_REPO\module-name` with `$env:APP_REPO` set to your multi-module app root.

### 1.2 Add an Angular module

1. Open **inventory.yaml**.
2. Under `components:`, add:

```yaml
- id: app-myapp
  type: module.angular
  name: My App
  group: frontend
  path: C:\dev\app\apps\myapp
  port: 4202
  command: ng serve
  # args: ["--port", "4202"]
```

3. Save. **Up** / **Up All** will run `ng serve` (or your `command`) in that directory in the background.

**Path:** Same as for Spring Boot: use an absolute path or a path relative to the Ignition repo root; for app modules in another repo, prefer `$env:APP_REPO\path\to\app`.

### 1.3 After adding a module

- Run **Generate-Config** if your app uses the generated `application.yml` or `environment.ts`, so the new module’s config (if any) is in sync. Copy generated files from `generated/` into the module if your workflow uses that.
- Use **Up** or **Up All** from the CLI or UI to start the new module with the rest of the stack.

---

## 2. How to switch broker (ActiveMQ vs Kafka)

Only one broker stack should run at a time. Switching = **inventory** + **Generate-Config**.

### 2.1 Set the active broker in inventory

1. Open **inventory.yaml**.
2. Under **defaults**, set `broker` to the one you want:
   - `broker: activemq` → use ActiveMQ (port 61616).
   - `broker: kafka` → use Kafka (port 9092).
3. Enable the matching broker component and disable the other (so **Up All** doesn’t start both):

```yaml
defaults:
  runtime: podman
  broker: kafka # or activemq

components:
  - id: broker-activemq
    type: infra
    name: ActiveMQ
    group: infra
    composeFile: compose/broker-activemq.yml
    enabled: false # set false when using Kafka

  - id: broker-kafka
    type: infra
    name: Kafka
    group: infra
    composeFile: compose/broker-kafka.yml
    enabled: true # set true when using Kafka
```

4. Save.

### 2.2 Regenerate config and restart

1. Run **Generate-Config** (CLI or UI). This regenerates `application.yml` and `environment.ts` from the inventory so broker URLs and options match `defaults.broker`.
2. If the old broker was running, run **Down** for that component (or **Down All**), then **Up** for the new broker (or **Up All**).

Result: apps get the correct broker URL (ActiveMQ or Kafka) from the generated config.

---

## 3. How to use the CLI

The CLI is **Ignition.ps1** in the `scripts/` folder. Run it from the **Ignition repo root** (or set `$env:IGNITION_REPO` to that path).

### 3.1 Commands

| Command                      | Meaning                                                                                         |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| **Status**                   | List all components (id, name, type, detail).                                                   |
| **Up**                       | Start all enabled components (Compose-based first, then module processes).                      |
| **Up -ComponentId \<id\>**   | Start only this component (compose or module).                                                  |
| **Down**                     | Stop all Compose-based components and all module processes (using `.ignition/run/<id>.pid`). |
| **Down -ComponentId \<id\>** | Stop this component (Compose-based or module; for a module, stops the process by PID).          |
| **Generate-Config**          | Run Ansible in WSL to generate `application.yml` and `environment.ts` into `generated/`.        |

**Down and module processes:** Down (and Down All) stops **Compose-based** components first, then stops **module processes** (Spring Boot, Angular) by reading `.ignition/run/<component-id>.pid` and terminating that process. Down -ComponentId \<module-id\> stops only that module’s process.

### 3.2 Examples

```powershell
# From Ignition repo root
.\scripts\Ignition.ps1 -Command Status
.\scripts\Ignition.ps1 -Command Up
.\scripts\Ignition.ps1 -Command Up -ComponentId broker-activemq
.\scripts\Ignition.ps1 -Command Down -ComponentId keycloak
.\scripts\Ignition.ps1 -Command Generate-Config
```

### 3.3 Prerequisites

- **Inventory:** `inventory.yaml` (or .yml / .json) at repo root. For YAML: `Install-Module powershell-yaml` or WSL with Python and PyYAML.
- **Generate-Config:** WSL with Ansible installed; repo path reachable from WSL (e.g. via `wslpath` when repo is on C:).
- **Compose:** Docker or Podman and Compose installed; runtime selected via inventory `defaults.runtime` or `$env:DOCKER_OR_PODMAN`.

---

## 4. How to use the UI

The UI is a local web app served by a **Python (FastAPI)** server. **Start-IgnitionUI.ps1** launches it (Windows). You can also run the server directly with Python.

### 4.1 Start the UI

From the Ignition repo root:

**Option A — PowerShell (Windows):**

```powershell
.\scripts\Start-IgnitionUI.ps1
```

Optional: `-RepoRoot C:\path\to\ignition` and `-Port 9080` (default port).

**Option B — Shell (macOS/Linux):**

```bash
./scripts/start-ignition-ui.sh
```

Optional: `--repo-root /path/to/ignition` and `--port 9080`. Run `chmod +x scripts/start-ignition-ui.sh` once if needed.

**Option C — Python (any OS):**

```bash
python -m ignition.server --repo-root . --port 9080
```

(Ensure you run from the folder that contains `ignition/`, or set `PYTHONPATH`.)

**Option D — Desktop window:** Install PyWebView (`pip install pywebview`), then run:

```bash
python scripts/launch_ui_window.py
```

This opens the UI in a native window instead of the browser.

Then open in a browser: **http://localhost:9080/** (unless you used a different port).  
If port 9080 is already in use, start with a different port (e.g. `-Port 9081`) and open the corresponding URL.

### 4.2 What you see

- **Table:** All components from the inventory (id, name, type, detail such as compose file or path).
- **Toolbar:** **Up All**, **Down All**, **Generate-Config**, **Refresh**.
- **Per row:** **Up** (start this component), **Down** (stop this component; only for compose-based infra/monitoring).
- **Output area:** Shows CLI output (or errors) after you run a command.

### 4.3 Same behaviour as CLI

The UI server runs the same **ignition** CLI (Python) for commands. Up/Down/Generate-Config behave the same as in the CLI; the UI is another way to trigger them and to see the component list.

---

## 5. Quick reference

| Task                   | Action                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------ |
| Add Spring Boot module | Add entry with `type: module.springboot`, `path`, optional `command`/`profile`/`args` to inventory.          |
| Add Angular module     | Add entry with `type: module.angular`, `path`, optional `command`/`args` to inventory.                       |
| Switch to ActiveMQ     | Set `defaults.broker: activemq`, enable `broker-activemq`, disable `broker-kafka`, run Generate-Config.      |
| Switch to Kafka        | Set `defaults.broker: kafka`, enable `broker-kafka`, disable `broker-activemq`, run Generate-Config.         |
| Start everything       | CLI: `Ignition.ps1 -Command Up`. UI: **Up All**.                                                              |
| Regenerate config      | CLI: `Ignition.ps1 -Command Generate-Config`. UI: **Generate-Config**.                                        |
| Stop module processes  | Down / Down All stops them via `.ignition/run/<id>.pid`. Or Down -ComponentId \<id\> for a single module. |
