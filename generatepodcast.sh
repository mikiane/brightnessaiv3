#!/bin/bash

# Génération quotidienne du podcast IA
# - Utilise le venv global /home/michel/myenv
# - Se place dans /home/michel/brightnessaiv3
# - Exécute le script Python en mode module et loggue la sortie

#set -euo pipefail

VENV="/home/michel/myenv"
REPO="/home/michel/brightnessaiv3"
PYTHON="$VENV/bin/python"
LOG_DIR="$REPO/docs"
LOG_FILE="$LOG_DIR/generatepodcast_ai.log"

mkdir -p "$LOG_DIR"

export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8
export PYTHONPATH="$REPO:$REPO/libs"

cd "$REPO"

echo "[$(date +'%F %T')] DÉMARRAGE generatepodcast.sh (AI)" >> "$LOG_FILE"
"$PYTHON" -m agent.auto_genpodcast_ai >> "$LOG_FILE" 2>&1
echo "[$(date +'%F %T')] FIN generatepodcast.sh (AI)" >> "$LOG_FILE"

# Pour activer d'autres podcasts, décommentez si besoin :
# echo "[$(date +'%F %T')] DÉMARRAGE generatepodcast.sh (GEO)" >> "$LOG_FILE"
# "$PYTHON" -m agent.auto_genpodcast_geo >> "$LOG_FILE" 2>&1
# echo "[$(date +'%F %T')] FIN generatepodcast.sh (GEO)" >> "$LOG_FILE"

# echo "[$(date +'%F %T')] DÉMARRAGE generatepodcast.sh (WEEKLY AI)" >> "$LOG_FILE"
# "$PYTHON" -m agent.auto_genweekpodcast_ai >> "$LOG_FILE" 2>&1
# echo "[$(date +'%F %T')] FIN generatepodcast.sh (WEEKLY AI)" >> "$LOG_FILE"


