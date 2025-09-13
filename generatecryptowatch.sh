#!/bin/bash

# Veille crypto quotidienne
# - Utilise le venv global /home/michel/myenv
# - Se place dans /home/michel/brightnessaiv3
# - Exécute les scripts Python en mode module et loggue la sortie

#set -euo pipefail

VENV="/home/michel/myenv"
REPO="/home/michel/brightnessaiv3"
PYTHON="$VENV/bin/python"
LOG_DIR="$REPO/docs"
LOG_FILE="$LOG_DIR/generatecryptowatch.log"

mkdir -p "$LOG_DIR"
mkdir -p "/home/michel/datas"

export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8
export PYTHONPATH="$REPO:$REPO/libs"
# Corrige les chemins attendus par certains scripts Python
export LOCALPATH="$REPO/"

cd "$REPO"

echo "[$(date +'%F %T')] DÉMARRAGE generatecryptowatch.sh (JSON)" >> "$LOG_FILE"
"$PYTHON" -m agent.auto_watch_crypto_json >> "$LOG_FILE" 2>&1
echo "[$(date +'%F %T')] FIN generatecryptowatch.sh (JSON)" >> "$LOG_FILE"

echo "[$(date +'%F %T')] DÉMARRAGE generatecryptowatch.sh (WATCH)" >> "$LOG_FILE"
"$PYTHON" -m agent.auto_watch_crypto >> "$LOG_FILE" 2>&1
echo "[$(date +'%F %T')] FIN generatecryptowatch.sh (WATCH)" >> "$LOG_FILE"


