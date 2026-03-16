# Elasticsearch: injecting data and restoring snapshots

This fits the Ignition architecture: **Compose** runs Elasticsearch (and Kibana); **Ansible** automates repeatable tasks (config generation already; snapshot register/restore here). You can copy/paste snapshot data on the host and restore via a playbook.

---

## 1. Snapshot restore (recommended)

**Flow:** Put your snapshot repository contents into `data/elasticsearch-snapshots/` on the host (copy/paste or extract an archive). That directory is bind-mounted into the container at `/usr/share/elasticsearch/snapshots`. Run the Ansible playbook to register the repository and restore a snapshot.

### Steps

1. **Start Elasticsearch** (so the API is up):

   ```powershell
   .\scripts\Ignition.ps1 -Command Up -ComponentId elasticsearch
   ```

2. **Put snapshot data in place**  
   Copy your snapshot repo folder (the one that contains the `indices`, `meta-*.dat`, `snap-*.dat`, etc.) into:

   ```
   <repo-root>/data/elasticsearch-snapshots/
   ```

   Or extract a backup archive there. The path inside the container will be `/usr/share/elasticsearch/snapshots`.

3. **Register repo and restore** (from repo root; Ansible in WSL or on PATH):

   ```bash
   ansible-playbook ansible/playbooks/elasticsearch-snapshot-restore.yml
   ```

   This registers a repository named `local_repo` pointing at that path. To restore a specific snapshot:

   ```bash
   ansible-playbook ansible/playbooks/elasticsearch-snapshot-restore.yml -e "snapshot_name=my_snapshot"
   ```

   Optional: custom repo name or only certain indices:

   ```bash
   ansible-playbook ansible/playbooks/elasticsearch-snapshot-restore.yml -e "snapshot_repo=my_repo snapshot_name=backup_1"
   ansible-playbook ansible/playbooks/elasticsearch-snapshot-restore.yml -e "snapshot_name=backup_1 restore_indices=my_index_1,my_index_2"
   ```

4. **Check progress** in Kibana (Index Management) or via `GET _cat/recovery`.

---

## 2. Copy/paste data folders (what goes where)

- **Snapshot repo contents:** Use `data/elasticsearch-snapshots/` as above. This is for Elasticsearch’s **snapshot/restore** feature (repository contents, not arbitrary files). The playbook registers this path as a fs repository and runs restore.
- **Full data directory (advanced):** If you have a full copy of an Elasticsearch **data directory** (node data path) and want to “paste” it in:
  - The default Compose setup uses a **named volume** for `data`, so you cannot copy into it from the host.
  - To inject a full data dir, use a **bind mount** for the data directory: e.g. add an override or a second compose file that mounts `./data/elasticsearch-data:/usr/share/elasticsearch/data`. Stop Elasticsearch, replace the contents of `./data/elasticsearch-data` with your backup, then start again. This is version-sensitive and not recommended unless you know the ES version matches.

So for “copy and paste data folders” in the intended way: use **snapshot data** in `data/elasticsearch-snapshots/` and the playbook; that respects the architecture (Compose + Ansible, no ad‑hoc volume hacks).

---

## 3. Architecture alignment

| Concern            | How it’s done                                                             |
| ------------------ | ------------------------------------------------------------------------- |
| Run Elasticsearch  | Compose (`elasticsearch-kibana.yml`); Ignition **Up** / **Down**       |
| Snapshot repo path | Bind mount `./data/elasticsearch-snapshots` → container; `path.repo` set  |
| Register + restore | Ansible playbook `elasticsearch-snapshot-restore.yml` (localhost, ES API) |
| Config generation  | Existing Ansible + Jinja (Generate-Config)                                |

No change to the CLI contract: snapshot restore is a separate Ansible step you run when you need it (or you could later add a Ignition command that invokes this playbook).

---

## 4. Create a snapshot (for backup or moving data)

To create a snapshot into the same repo (so you can copy `data/elasticsearch-snapshots` elsewhere or restore later):

1. Ensure the repo is registered (run the playbook once without `snapshot_name`, or after a restore).
2. Call the API (e.g. from WSL or PowerShell with curl):
   ```bash
   curl -X PUT "http://localhost:9200/_snapshot/local_repo/my_backup?wait_for_completion=true"
   ```
   Snapshots will be written to `data/elasticsearch-snapshots/` on the host.
