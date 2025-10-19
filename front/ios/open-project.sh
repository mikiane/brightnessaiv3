#!/bin/bash
#
# Script d'ouverture du projet BrightnessChat iOS
# Usage: ./open-project.sh
#

echo "🚀 Ouverture du projet BrightnessChat..."
echo ""

# Vérifier que Xcode est installé
if ! command -v xed &> /dev/null; then
    echo "❌ Erreur: Xcode n'est pas installé"
    echo "   Installez Xcode depuis l'App Store"
    exit 1
fi

# Vérifier que le projet existe
if [ ! -f "BrightnessChat/BrightnessChat.xcodeproj/project.pbxproj" ]; then
    echo "❌ Erreur: Projet Xcode introuvable"
    echo "   Assurez-vous d'être dans le répertoire front/ios/"
    exit 1
fi

# Ouvrir le projet
echo "✅ Ouverture du projet dans Xcode..."
open BrightnessChat/BrightnessChat.xcodeproj

echo ""
echo "📝 N'oubliez pas de :"
echo "   1. Vérifier la configuration dans AppConfig.swift"
echo "   2. Attendre le téléchargement de MarkdownUI"
echo "   3. Sélectionner un simulateur"
echo "   4. Appuyer sur ▶️ pour lancer"
echo ""
echo "📚 Documentation :"
echo "   - QUICKSTART.md : Démarrage rapide"
echo "   - README.md : Documentation complète"
echo "   - TECHNICAL.md : Détails techniques"
echo ""
echo "✨ Bon développement !"

