# Inventory schema (Ignition)

Single source of truth for all controllable components: infra, application modules, and (later) monitoring stacks. The CLI and UI discover components from this schema; no hardcoded component types in code.

---

## Top-level structure

- **Single file**: One YAML file (e.g. `inventory.yaml` or `inventory.yml`) at repo root or under a config folder.
- **Alternative**: A folder of small YAML/JSON files (e.g. `inventory.d/*.yaml`) merged at load time; each file can define one or more components or a group.

Example single-file shape:

```yaml
# Optional: global defaults (runtime, paths, broker choice)
defaults:
  runtime: podman # docker | podman
  broker: activemq # activemq | kafka

# List of components; order can be used for display or startup order
components: []
```

---

## Component entry (common fields)

Every component **must** have:

| Field  | Type   | Required | Description                                                                                                                                    |
| ------ | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`   | string | Yes      | Unique identifier (e.g. `broker-activemq`, `service-auth`, `app-gateway`). Used in CLI and for references.                                     |
| `type` | string | Yes      | Component kind. Known values: `infra`, `module.springboot`, `module.angular`, `monitoring`. Schema is open: add new types without code change. |
| `name` | string | Yes      | Human-readable label (e.g. "ActiveMQ", "Auth Service", "Gateway UI").                                                                          |

Optional **common** fields:

| Field     | Type   | Required | Description                                                                                            |
| --------- | ------ | -------- | ------------------------------------------------------------------------------------------------------ |
| `group`   | string | No       | Logical group (e.g. `infra`, `backend`, `frontend`, `monitoring`). Used for "Up group" or UI grouping. |
| `enabled` | bool   | No       | If `false`, component is skipped by "Up All" and hidden or disabled in UI. Default: `true`.            |

---

## Type: `infra`

Containerized infrastructure (broker, Elasticsearch, Kibana, Keycloak, etc.). Started via Compose (Docker or Podman).

| Field         | Type   | Required | Description                                                                                                               |
| ------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| `composeFile` | string | Yes      | Path to Compose file relative to repo root or absolute (e.g. `compose/broker-activemq.yml`, `compose/elasticsearch.yml`). |
| `runtime`     | string | No       | Override global runtime: `docker` or `podman`. If omitted, use `defaults.runtime`.                                        |
| `projectName` | string | No       | Compose project name (optional; default from compose file or directory name).                                             |

Example:

```yaml
- id: broker-activemq
  type: infra
  name: ActiveMQ
  group: infra
  composeFile: compose/broker-activemq.yml

- id: elasticsearch
  type: infra
  name: Elasticsearch
  group: infra
  composeFile: compose/elasticsearch.yml
  runtime: podman
```

---

## Type: `module.springboot`

Spring Boot (Java) application module. Run as a process (e.g. `mvn spring-boot:run` or `java -jar`); path and command from inventory.

| Field     | Type   | Required | Description                                                                                                                                 |
| --------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`    | string | Yes      | Root directory of the module (absolute or relative to repo/env). On Windows e.g. `C:\dev\app\service-auth` or `$env:APP_REPO\service-auth`. |
| `port`    | int    | No       | Main HTTP port (for status/display).                                                                                                        |
| `command` | string | No       | Command to start (e.g. `mvn spring-boot:run`, `java -jar target/app.jar`). Default can be `mvn spring-boot:run` if not set.                 |
| `profile` | string | No       | Spring profile (e.g. `dev`, `local`). Passed to the command or generated config.                                                            |
| `args`    | list   | No       | Extra arguments (e.g. `-Dserver.port=8081`).                                                                                                |

Example:

```yaml
- id: service-auth
  type: module.springboot
  name: Auth Service
  group: backend
  path: C:\dev\app\service-auth
  port: 8081
  command: mvn spring-boot:run
  profile: dev
```

---

## Type: `module.angular`

Angular application module. Run as a process (e.g. `ng serve`).

| Field     | Type   | Required | Description                                                                            |
| --------- | ------ | -------- | -------------------------------------------------------------------------------------- |
| `path`    | string | Yes      | Root directory of the Angular app (absolute or relative).                              |
| `port`    | int    | No       | Dev server port (e.g. 4200).                                                           |
| `command` | string | No       | Command to start (e.g. `ng serve`, `npm start`). Default can be `ng serve` if not set. |
| `args`    | list   | No       | Extra arguments (e.g. `--port 4201`).                                                  |

Example:

```yaml
- id: app-gateway
  type: module.angular
  name: Gateway UI
  group: frontend
  path: C:\dev\app\apps\gateway
  port: 4200
  command: ng serve
```

---

## Type: `monitoring`

Containerized monitoring stack (e.g. Grafana, Prometheus). Same as `infra` in behaviour: started via Compose. Type exists so the UI/CLI can group or filter “monitoring” separately; extensible for future config generation (e.g. Prometheus scrape config).

| Field         | Type   | Required | Description                                           |
| ------------- | ------ | -------- | ----------------------------------------------------- |
| `composeFile` | string | Yes      | Path to Compose file (e.g. `compose/monitoring.yml`). |
| `runtime`     | string | No       | Override: `docker` or `podman`.                       |

Example:

```yaml
- id: monitoring
  type: monitoring
  name: Grafana + Prometheus
  group: monitoring
  composeFile: compose/monitoring.yml
  enabled: false
```

---

## Global `defaults` (optional)

| Field         | Type   | Description                                                                                                                 |
| ------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| `runtime`     | string | Default container runtime: `docker` or `podman`. Used by all `infra` and `monitoring` components that do not set `runtime`. |
| `broker`      | string | Active broker choice: `activemq` or `kafka`. Used by config generation (Ansible/Jinja) to select broker URL and templates.  |
| `appRepoPath` | string | Optional base path for module `path` when relative (e.g. `C:\dev\app` or `$env:APP_REPO`).                                  |

---

## Extensibility

- **New component type**: Add a new `type` value (e.g. `module.python`, `infra.redis`) and define the type-specific fields in this doc. CLI/UI should treat unknown types generically: show `id`, `name`, `type`; start/stop only if the type has a known execution model (compose vs process).
- **New fields**: Add optional fields to existing types as needed; code should ignore unknown fields or pass them through to config generation.
- **Multiple files**: If using `inventory.d/*.yaml`, each file can contain a YAML array of components or an object with `components: []` and optional `defaults`. Loader merges arrays and deep-merges defaults.

---

## Summary table (required vs optional by type)

| Field       | infra | module.springboot | module.angular | monitoring |
| ----------- | ----- | ----------------- | -------------- | ---------- |
| id          | Yes   | Yes               | Yes            | Yes        |
| type        | Yes   | Yes               | Yes            | Yes        |
| name        | Yes   | Yes               | Yes            | Yes        |
| group       | No    | No                | No             | No         |
| enabled     | No    | No                | No             | No         |
| composeFile | Yes   | —                 | —              | Yes        |
| runtime     | No    | —                 | —              | No         |
| projectName | No    | —                 | —              | —          |
| path        | —     | Yes               | Yes            | —          |
| port        | —     | No                | No             | —          |
| command     | —     | No                | No             | —          |
| profile     | —     | No                | —              | —          |
| args        | —     | No                | No             | —          |
