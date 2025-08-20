#!/bin/bash

# Script de déploiement pour Google Cloud
# Usage: ./deploy_to_gcloud.sh

echo "🚀 Déploiement de BrightnessAI v3 sur Google Cloud"

# Variables
PROJECT_DIR="/home/michel/brightnessaiv3"
VENV_PATH="/home/michel/myenv"
REPO_URL="https://github.com/mikiane/brightnessaiv3.git"

# Étape 1: Cloner le repository
echo "📦 Étape 1: Clonage du repository..."
if [ -d "$PROJECT_DIR" ]; then
    echo "Le dossier $PROJECT_DIR existe déjà. Mise à jour..."
    cd $PROJECT_DIR
    git pull origin main
else
    echo "Clonage du repository..."
    cd /home/michel
    git clone $REPO_URL
    cd $PROJECT_DIR
fi

# Étape 2: Créer l'environnement virtuel (global) si nécessaire
echo "🐍 Étape 2: Vérification/Création de l'environnement virtuel global à $VENV_PATH..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "Environnement virtuel global créé à $VENV_PATH."
else
    echo "L'environnement virtuel global existe déjà."
fi

# Étape 3: Activer l'environnement global et installer les dépendances du projet
echo "📚 Étape 3: Installation des dépendances dans $VENV_PATH..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Étape 4: Copier le fichier .env depuis l'ancien projet si nécessaire
echo "🔐 Étape 4: Configuration des variables d'environnement..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "/home/michel/brightnessaiv2/.env" ]; then
        echo "Copie du fichier .env depuis l'ancien projet..."
        cp /home/michel/brightnessaiv2/.env $PROJECT_DIR/.env
        echo "Fichier .env copié. Vérifiez les chemins et variables."
    else
        echo "⚠️  ATTENTION: Fichier .env non trouvé!"
        echo "Créez un fichier .env avec vos clés API et configurations."
    fi
else
    echo "Fichier .env déjà présent."
fi

# Étape 5: Créer les dossiers nécessaires
echo "📁 Étape 5: Création des dossiers nécessaires..."
mkdir -p $PROJECT_DIR/docs
mkdir -p $PROJECT_DIR/tmp
mkdir -p $PROJECT_DIR/datas

# Étape 6: Donner les permissions d'exécution aux scripts
echo "🔧 Étape 6: Configuration des permissions..."
chmod +x $PROJECT_DIR/start-all.sh
chmod +x $PROJECT_DIR/stop-all.sh
chmod +x $PROJECT_DIR/status-all.sh
chmod +x $PROJECT_DIR/create_virtualenv.sh

# Étape 7: Arrêter les anciens services si nécessaire
echo "🛑 Étape 7: Arrêt des anciens services..."
if [ -f "/home/michel/brightnessaiv2/stop-all.sh" ]; then
    echo "Arrêt des services de brightnessaiv2..."
    /home/michel/brightnessaiv2/stop-all.sh
fi

# Étape 8: Démarrer les nouveaux services
echo "✅ Étape 8: Démarrage des services..."
cd $PROJECT_DIR
./start-all.sh

# Vérification
echo "🔍 Vérification des services..."
sleep 3
./status-all.sh

echo "✨ Déploiement terminé!"
echo ""
echo "📝 Prochaines étapes:"
echo "1. Vérifiez le fichier .env et ajustez les variables si nécessaire"
echo "2. Testez les APIs:"
echo "   - http://[IP_SERVEUR]:8000 (Streaming API)"
echo "   - http://[IP_SERVEUR]:8001 (Transformers API)"
echo "   - http://[IP_SERVEUR]:8002 (Alter Brain API)"
echo "3. Configurez le cron pour les scripts automatiques si nécessaire"
echo ""
echo "Pour voir les logs:"
echo "  tail -f $PROJECT_DIR/docs/error.log"
