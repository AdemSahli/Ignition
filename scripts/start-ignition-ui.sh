#!/usr/bin/env bash
# Start Ignition web UI (Python FastAPI). Usage: ./start-ignition-ui.sh [--repo-root PATH] [--port PORT]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${IGNITION_REPO:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PORT=9080
while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-root) REPO_ROOT="$2"; shift 2 ;;
        --port) PORT="$2"; shift 2 ;;
        -h|--help) echo "Usage: $0 [--repo-root PATH] [--port PORT]"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
if [[ ! -d "$REPO_ROOT/ignition" ]]; then echo "ignition package not found under $REPO_ROOT" >&2; exit 1; fi
export PYTHONPATH="$REPO_ROOT"
cd "$REPO_ROOT"
echo "Ignition UI: http://127.0.0.1:${PORT}/ (RepoRoot: $REPO_ROOT). Press Ctrl+C to stop."
exec python3 -m ignition.server --repo-root "$REPO_ROOT" --port "$PORT"
