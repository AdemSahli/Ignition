# Setup and troubleshooting

**Use this doc when installing Ignition on a new machine or when something fails.** It is updated whenever we fix a new problem so you don’t get stuck on the same issues again.

---

## 1. Installation checklist (new computer)

### Windows

Do these in order. Run all **CLI and UI** commands from **Windows PowerShell** (not from inside WSL).

| Step | What to do                                                                                                                                                                                                                                                                                         | Verify                                                                           |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1    | Get the repo (copy or clone). Repo root = folder with `inventory.yaml`, `compose/`, `scripts/`, `ignition/`.                                                                                                                                                                                    | You have `scripts/Ignition.ps1` and `ignition/`.                               |
| 2    | Copy `inventory.example.yaml` to `inventory.yaml`. Edit `defaults.runtime`, `defaults.broker`, and each module’s `path`.                                                                                                                                                                           | File exists at repo root.                                                        |
| 3    | **Python 3:** Install Python 3 from python.org or Microsoft Store. Ensure `py -3` or `python` is on PATH.                                                                                                                                                                                          | `py -3 -c "import sys; print(sys.version)"` or `python --version` works.         |
| 4    | **CLI deps:** From repo root: `pip install -r requirements.txt` (or `py -3 -m pip install -r requirements.txt`). Do **not** use `pip3 install pyyaml` if you see “externally-managed-environment”.                                                                                                 | From **PowerShell**: `wsl python3 -c "import yaml; print('OK')"` prints OK.      |
| 5    | **Generate-Config (optional):** In **WSL**: `sudo apt update && sudo apt install ansible` (or `pip3 install --user ansible` if your distro allows it).                                                                                                                                             | From **PowerShell**: `wsl bash -c "command -v ansible-playbook"` returns a path. |
| 6    | **Up/Down (optional):** Install Docker or Podman + Compose. Set `defaults.runtime` in inventory or `$env:DOCKER_OR_PODMAN`.                                                                                                                                                                        | `docker compose version` or `podman compose version` works.                      |
| 7    | From repo root in **PowerShell**: `.\scripts\Ignition.ps1 -Command Status`                                                                                                                                                                                                                          | Table of components; no “YAML inventory requires” or “command not found”.        |
| 8    | **UI (optional):** `.\scripts\Start-IgnitionUI.ps1 -RepoRoot C:\path\to\repo` (launches Python server). Open http://localhost:9080/ Or run `python -m ignition.server --repo-root .` from repo root. For a desktop window: `pip install pywebview` then `python scripts/launch_ui_window.py`. | Component list loads; Up/Down per row work.                                      |

### macOS / Linux

| Step | What to do                                                                                                          | Verify                                                      |
| ---- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 1    | Get the repo. Repo root = folder with `inventory.yaml`, `compose/`, `scripts/`, `ignition/`.                     | You have `scripts/ignition` and `ignition/`.          |
| 2    | Copy `inventory.example.yaml` to `inventory.yaml`. Edit paths (use `$HOME` or relative paths for portability).      | File exists at repo root.                                   |
| 3    | **Python 3:** Use system Python or install (e.g. `sudo apt install python3 python3-pip` or Homebrew).               | `python3 --version` works.                                  |
| 4    | **CLI deps:** From repo root: `pip3 install -r requirements.txt` (or `python3 -m pip install -r requirements.txt`). | `python3 -c "import yaml; print('OK')"` prints OK.          |
| 5    | **Generate-Config (optional):** Install Ansible: `pip3 install ansible` or `sudo apt install ansible`.              | `ansible-playbook --version` works.                         |
| 6    | **Up/Down (optional):** Docker or Podman + Compose. Set `defaults.runtime` in inventory or `DOCKER_OR_PODMAN`.      | `docker compose version` or `podman compose version` works. |
| 7    | Make launcher executable (once): `chmod +x scripts/ignition`. From repo root: `./scripts/ignition status`     | Table of components.                                        |

---

## 2. Troubleshooting

### "Python 3 not found" (Windows launcher)

- **Cause:** Neither `py`, `python`, nor `python3` found on PATH.
- **Fix:** Install Python 3 from python.org or Microsoft Store; during setup check "Add Python to PATH". Or use the Windows Store "Python 3.12" app.

### "No module named yaml" / "YAML inventory requires PyYAML"

- **Cause:** PyYAML is not installed for the Python used by the CLI.
- **Fix:** From repo root run: `pip install -r requirements.txt` (or `py -3 -m pip install -r requirements.txt` on Windows, `pip3 install -r requirements.txt` on macOS/Linux). Use the same Python that the launcher uses.

### "YAML inventory requires…" / "bash: unexpected EOF…" (legacy)

- **Cause:** Old PowerShell-only setup: inventory is YAML but PowerShell had no `powershell-yaml` and WSL YAML failed.
- **Fix:** The CLI is now Python-based; install Python 3 and run `pip install -r requirements.txt` (see above). No PowerShell-YAML or WSL needed for inventory.

### “Command 'wsl' not found”

- **Cause:** You ran the command **inside** a WSL/Linux terminal. `wsl` is a **Windows** command.
- **Fix:** Run the Ignition CLI and UI from **Windows PowerShell** (or Windows Terminal with PowerShell). Use WSL only for installing packages (e.g. `python3-yaml`, `ansible`).

### “externally-managed-environment” when running `pip3 install pyyaml`

- **Cause:** Your Linux distro (e.g. Debian/Ubuntu) restricts system-wide pip to avoid breaking the OS Python.
- **Fix:** Use the system package: `sudo apt update && sudo apt install -y python3-yaml`. Do **not** use `pip3 install pyyaml` or `--break-system-packages`.

### “Invalid command. Allowed: Up, Down, Generate-Config, Status.” (UI when clicking Up on a component)

- **Cause:** The UI or API sent a command the CLI didn’t accept (e.g. wrong casing, extra spaces, or parameter binding issue).
- **Fix:** Restart the UI script so it uses the latest API (command normalization and splatting). If it still happens, run the same action from PowerShell: `.\scripts\Ignition.ps1 -Command Up -ComponentId broker-activemq`.

### “ansible-playbook: command not found” / “Ansible not found in WSL”

- **Cause:** Ansible is not installed in WSL or not on PATH.
- **Fix:** Inside **WSL** run: `sudo apt update && sudo apt install ansible`. Or `pip3 install --user ansible` if your distro allows it. Then run **Generate-Config** again from **Windows PowerShell**.

### “[WARNING]: No inventory was parsed, only implicit localhost is available”

- **Cause:** Generate-Config was (or is) running Ansible without an explicit inventory file, so Ansible reports that it only has implicit localhost.
- **Fix:** The CLI now passes `-i inventory.yaml` when calling `ansible-playbook`. Ensure you run **Generate-Config** from the repo root (where `inventory.yaml` exists), or pass `-RepoRoot` to the script. If you run the playbook manually from WSL, use: `ansible-playbook ansible/playbooks/generate-config.yml -i inventory.yaml`.

### Status table looks garbled or overlapping

- **Cause:** Column widths or long values without truncation.
- **Fix:** The script now uses fixed column widths and truncates long values with `...`. If your terminal is narrow, resize the window or ignore wrapping.

### Repo root / inventory not found

- **Cause:** You ran the script from a directory that isn’t the Ignition repo root, or the path doesn’t contain `inventory.yaml` / `inventory.yml` / `inventory.json`.
- **Fix:** Run from the repo root (the folder that contains `inventory.yaml` and `scripts/`), or pass `-RepoRoot C:\path\to\ignition` explicitly. For the UI, always pass `-RepoRoot` when starting the script.

### UI port 9080 already in use

- **Fix:** Start the UI with another port: `.\scripts\Start-IgnitionUI.ps1 -RepoRoot C:\path\to\repo -Port 9081` or `python -m ignition.server --repo-root . --port 9081`. Open http://localhost:9081/

### How do I see logs for modules (Spring Boot / Angular)?

- **Cause:** By default, modules run in a hidden CMD window, so you don’t see their output.
- **Fix (choose one):**
  1. **Visible console per module:**  
     `.\scripts\Ignition.ps1 -Command Up -ShowModuleConsole`  
     A CMD window opens for each started module so you can see logs there.
  2. **Log to file (no extra windows):**  
     `.\scripts\Ignition.ps1 -Command Up -LogModuleToFile`  
     Output is written to `.ignition\run\<component-id>.log`. To watch logs:  
     `Get-Content .ignition\run\service-auth.log -Wait -Tail 50`

---

## 3. Running on macOS / Linux

- **Entry point:** `./scripts/ignition` (run from repo root). First time: `chmod +x scripts/ignition`.
- **Commands:** `./scripts/ignition status`, `./scripts/ignition up`, `./scripts/ignition down`, `./scripts/ignition generate-config`. Optional: `--component-id <id>`, `--all`, `--show-module-console`, `--log-module-to-file` (for `up`).
- **Repo root:** Set `IGNITION_REPO` to the repo path, or run from the repo root directory.
- **Generate-Config:** Uses Ansible from PATH (no WSL). Install with `pip3 install ansible` or `sudo apt install ansible`.

## 4. Where to run what

| Action                                              | Where to run it                                            |
| --------------------------------------------------- | ---------------------------------------------------------- |
| Install Python 3, pip install -r requirements.txt   | **Windows:** PowerShell or cmd. **macOS/Linux:** terminal. |
| Install ansible (for Generate-Config)               | **Windows:** WSL. **macOS/Linux:** terminal (pip3 or apt). |
| Run Ignition.ps1 (Status, Up, Down, Generate-Config) | **Windows PowerShell**                                     |
| Run scripts/ignition                             | **macOS/Linux** (from repo root)                           |
| Start Start-IgnitionUI.ps1                        | **Windows PowerShell**                                     |
| Open the UI in a browser                            | Any browser on Windows                                     |

---

## 5. Quick reference

- **Runbooks (add module, switch broker, CLI/UI):** [runbooks.md](runbooks.md)
- **Test steps:** [test-checklist.md](test-checklist.md)
- **Repo layout:** [../ignition-repo-layout.md](../ignition-repo-layout.md)
- **Main README:** [../README.md](../README.md)

**Rule of thumb:** Install things **in WSL** (python3-yaml, ansible). **Run** the Ignition scripts **from Windows PowerShell**.
