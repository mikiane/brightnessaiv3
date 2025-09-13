#!/usr/bin/env bash

# Lancement de la veille crypto
# - Exécute successivement:
#   1) agent/auto_watch_crypto_json.py (génère /home/michel/datas/latest.json)
#   2) agent/auto_watch_crypto.py (autres traitements)

set -uo pipefail

timestamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Utilise PYTHON si défini, sinon python3
PY_BIN="${PYTHON:-python3}"

run_step() {
  local script_path="$1"
  echo "[$(timestamp)] ▶︎ Lancement: $script_path"
  if "$PY_BIN" "$script_path"; then
    echo "[$(timestamp)] ✅ Terminé:  $script_path"
  else
    rc=$?
    echo "[$(timestamp)] ❌ Erreur ($rc): $script_path"
    # On continue malgré l'erreur pour lancer l'étape suivante
  fi
}

run_step "agent/auto_watch_crypto_json.py"
run_step "agent/auto_watch_crypto.py"

echo "[$(timestamp)] ✅ Workflow generatecryptowatch terminé"


