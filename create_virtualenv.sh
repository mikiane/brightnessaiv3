#!/bin/bash

# Définition du chemin de l'environnement virtuel
VENV_PATH="/home/michel/brightnessaiv2/brightnessaiv2"

# Définition du chemin vers requirements.txt
REQUIREMENTS_PATH="requirements.txt"

# Création de l'environnement virtuel si celui-ci n'existe pas
if [ ! -d "$VENV_PATH" ]; then
    echo "Création de l'environnement virtuel à $VENV_PATH"
    python3 -m venv "$VENV_PATH"
else
    echo "L'environnement virtuel existe déjà."
fi

# Activation de l'environnement virtuel
source "$VENV_PATH/bin/activate"

# Définition de PYTHONPATH de manière permanente pour l'environnement virtuel
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_SITE_PACKAGES="$VENV_PATH/lib/python$PYTHON_VERSION/site-packages"
EXPORT_COMMAND="export PYTHONPATH=$PYTHON_SITE_PACKAGES:\$PYTHONPATH"

if ! grep -Fxq "$EXPORT_COMMAND" "$VENV_PATH/bin/activate"; then
    echo "Ajout de PYTHONPATH à $VENV_PATH/bin/activate"
    echo $EXPORT_COMMAND >> "$VENV_PATH/bin/activate"
else
    echo "PYTHONPATH déjà défini dans $VENV_PATH/bin/activate"
fi

# Vérification de l'existence de requirements.txt
if [ ! -f "$REQUIREMENTS_PATH" ]; then
    echo "Le fichier requirements.txt est introuvable à $REQUIREMENTS_PATH"
    deactivate
    exit 1
fi

# Installation des dépendances à partir de requirements.txt
echo "Installation des dépendances depuis requirements.txt..."
pip install -r "$REQUIREMENTS_PATH"

echo "L'environnement virtuel est prêt et les dépendances sont installées."

# Désactivation de l'environnement virtuel
deactivate
