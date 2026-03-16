# Ignition repo layout (target structure)

Suggested layout for the **Ignition** repo. Scripts and config under `workspace/artifacts/` are the reference implementation; copy or move them into the real repo when it is created.

---

## Directory structure

```
ignition/                       # Repo root (separate from multi-module app)
├── inventory.yaml
├── inventory.example.yaml
├── config/
├── compose/
│   ├── broker-activemq.yml
│   ├── broker-kafka.yml
│   ├── elasticsearch-kibana.yml
│   ├── keycloak.yml
│   └── monitoring.yml
├── ignition/                   # Python package (CLI core, UI server)
│   ├── cli.py
│   ├── server.py
│   ├── inventory.py
│   ├── compose.py
│   ├── modules.py
│   ├── runtime.py
│   └── ...
├── scripts/
│   ├── Ignition.ps1
│   ├── ignition
│   ├── Start-IgnitionUI.ps1
│   ├── start-ignition-ui.sh
│   ├── smoke-test-ui.ps1
│   └── launch_ui_window.py
├── ansible/
├── ui/
│   └── index.html
└── docs/
```

---

## Scripts and Python core

- **Ignition.ps1** (Windows) / **ignition** (macOS/Linux) — Launch the Python CLI: `python -m ignition.cli`.
- **Start-IgnitionUI.ps1** — Launches the Python UI server (FastAPI) on port 9080.
- **smoke-test-ui.ps1** — Automated smoke test for the UI.

---

## Inventory location

- **Repo root:** `inventory.yaml` or `inventory.yml`. Alternatively `config/inventory.yaml` with `IGNITION_INVENTORY` or CLI parameter.

---

## Compose files

- All under `compose/`; paths in inventory are relative to repo root. The Python CLI (`ignition.compose`) runs `docker compose` or `podman compose` based on inventory `defaults.runtime` or `DOCKER_OR_PODMAN`.
