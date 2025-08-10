#!/bin/bash

# Définir le chemin de l'environnement virtuel
VENV_PATH="/home/michel/myenv"
GUNICORN="${VENV_PATH}/bin/gunicorn"

# Lancement de Gunicorn avec la configuration spécifique
${GUNICORN} --bind 0.0.0.0:8000 -w 8 api.streaming_api:app --timeout 14400 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output

${GUNICORN} --bind 0.0.0.0:8001 -w 8 api.transformers_api:app --timeout 14400 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output

${GUNICORN} --bind 0.0.0.0:8002 -w 8 api.alter_brain_api:app --timeout 14400 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output