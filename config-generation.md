# Config generation (Ansible + Jinja on WSL)

Config files (`application.yml`, `environment.ts`) are generated from the **Ignition inventory** so broker choice, Elasticsearch URL, Keycloak URL, etc. stay in one place. Ansible + Jinja run **inside WSL**; the PowerShell CLI invokes them via `wsl ansible-playbook ...`.

---

## Approach

1. **Source of truth:** `inventory.yaml` at repo root. `defaults.broker` (`activemq` | `kafka`) and optional `defaults` drive which broker URL and options are rendered.
2. **Playbook:** `ansible/playbooks/generate-config.yml` runs on **localhost** (no SSH). It loads the inventory with `include_vars`, derives URLs (broker, Elasticsearch, Keycloak), and runs the Jinja templates.
3. **Templates:**
   - `ansible/templates/application.yml.j2` → Spring Boot `application.yml` (broker, Elasticsearch, Keycloak, server port).
   - `ansible/templates/environment.ts.j2` → Angular `environment.ts` (apiUrl, keycloak, elasticsearchUrl, broker).
4. **Output:** Files are written to `generated/` at repo root (`generated/application.yml`, `generated/environment.ts`). You can copy them into each module or use them as reference; a future CLI step could copy per-module from inventory paths.

---

## Running from WSL

From a WSL shell (repo root is current dir or set `repo_root`):

```bash
cd /path/to/Ignition
ansible-playbook ansible/playbooks/generate-config.yml
```

If the inventory is not at `repo_root/inventory.yaml`, pass it:

```bash
ansible-playbook ansible/playbooks/generate-config.yml -e "repo_root=/path/to/Ignition"
```

---

## Running from PowerShell (Windows)

The CLI or a helper script should invoke WSL and run the playbook. Example:

```powershell
$repoRoot = "C:\dev\Ignition"
$wslPath = wsl wslpath -a $repoRoot
wsl -e bash -c "cd $wslPath && ansible-playbook ansible/playbooks/generate-config.yml"
```

Or if the repo is already in WSL (e.g. `~/Ignition`):

```powershell
wsl -e bash -c "cd ~/Ignition && ansible-playbook ansible/playbooks/generate-config.yml"
```

Ensure **Ansible is installed in WSL** (e.g. `sudo apt install ansible` or `pip install ansible` in a venv).

---

## Variables used in templates

| Variable            | Source                          | Description                                                    |
| ------------------- | ------------------------------- | -------------------------------------------------------------- |
| `broker`            | `defaults.broker` in inventory  | `activemq` or `kafka`                                          |
| `broker_url`        | Derived                         | `tcp://localhost:61616` (ActiveMQ) or `localhost:9092` (Kafka) |
| `elasticsearch_url` | Fixed (or from inventory later) | `http://localhost:9200`                                        |
| `keycloak_url`      | Fixed (or from inventory later) | `http://localhost:8080`                                        |

If the inventory file is missing or doesn’t define `defaults`, the playbook falls back to `broker: activemq` and the URLs above.

---

## Adding new config kinds (scalability)

To generate more file types (e.g. Prometheus `prometheus.yml`, Grafana datasources):

1. Add a new Jinja template under `ansible/templates/` (e.g. `prometheus.yml.j2`).
2. Add a task in `generate-config.yml` that uses `ansible.builtin.template` with the new template and destination under `generated/` or a path from inventory.
3. Add any new variables to the playbook (from `ignition.defaults` or `ignition.components`) and use them in the template.

No change to the “run config generation” contract: one playbook, invoked the same way from WSL/PowerShell.
