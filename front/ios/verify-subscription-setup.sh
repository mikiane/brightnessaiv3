#!/bin/bash

# Script de vérification de la configuration de l'abonnement
# Brightness Chat - Subscription Setup Checker

echo "🔍 Vérification de la configuration de l'abonnement..."
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
ERRORS=0
WARNINGS=0
SUCCESS=0

# Fonction pour vérifier l'existence d'un fichier
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((SUCCESS++))
    else
        echo -e "${RED}❌${NC} $2 (fichier manquant: $1)"
        ((ERRORS++))
    fi
}

# Fonction pour vérifier le contenu d'un fichier
check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $3"
        ((SUCCESS++))
    else
        echo -e "${YELLOW}⚠️${NC}  $3"
        ((WARNINGS++))
    fi
}

echo "📁 Vérification des fichiers créés..."
echo ""

# Vérifier les Models
check_file "BrightnessChat/BrightnessChat/Models/AuthenticationManager.swift" "AuthenticationManager.swift"
check_file "BrightnessChat/BrightnessChat/Models/SubscriptionManager.swift" "SubscriptionManager.swift"
check_file "BrightnessChat/BrightnessChat/Models/UsageManager.swift" "UsageManager.swift"

echo ""

# Vérifier les Views
check_file "BrightnessChat/BrightnessChat/Views/LoginView.swift" "LoginView.swift"
check_file "BrightnessChat/BrightnessChat/Views/SubscriptionView.swift" "SubscriptionView.swift"
check_file "BrightnessChat/BrightnessChat/Views/SettingsView.swift" "SettingsView.swift"

echo ""

# Vérifier la configuration StoreKit
check_file "BrightnessStore.storekit" "BrightnessStore.storekit"

echo ""
echo "📄 Vérification des fichiers modifiés..."
echo ""

# Vérifier les modifications dans les fichiers existants
check_content "BrightnessChat/BrightnessChat/App/BrightnessChatApp.swift" "AuthenticationManager" "BrightnessChatApp.swift contient AuthenticationManager"
check_content "BrightnessChat/BrightnessChat/App/BrightnessChatApp.swift" "SubscriptionManager" "BrightnessChatApp.swift contient SubscriptionManager"
check_content "BrightnessChat/BrightnessChat/App/BrightnessChatApp.swift" "UsageManager" "BrightnessChatApp.swift contient UsageManager"

echo ""

check_content "BrightnessChat/BrightnessChat/ViewModels/ChatViewModel.swift" "showSubscriptionView" "ChatViewModel.swift contient showSubscriptionView"
check_content "BrightnessChat/BrightnessChat/ViewModels/ChatViewModel.swift" "canMakeRequest" "ChatViewModel.swift vérifie le quota"
check_content "BrightnessChat/BrightnessChat/ViewModels/ChatViewModel.swift" "incrementRequestCount" "ChatViewModel.swift incrémente le compteur"

echo ""

check_content "BrightnessChat/BrightnessChat/Views/ChatView.swift" "SettingsView" "ChatView.swift contient SettingsView"
check_content "BrightnessChat/BrightnessChat/Views/ChatView.swift" "showSettings" "ChatView.swift affiche les paramètres"

echo ""

check_content "BrightnessChat/BrightnessChat/Views/ComposerView.swift" "usageMessage" "ComposerView.swift affiche le quota"

echo ""
echo "🔑 Vérification du Product ID..."
echo ""

# Vérifier que le Product ID est cohérent
PRODUCT_ID="com.brightness.chat.monthly"

check_content "BrightnessChat/BrightnessChat/Models/SubscriptionManager.swift" "$PRODUCT_ID" "Product ID dans SubscriptionManager.swift"
check_content "BrightnessStore.storekit" "$PRODUCT_ID" "Product ID dans BrightnessStore.storekit"

echo ""
echo "📚 Vérification de la documentation..."
echo ""

check_file "CONFIGURATION-ABONNEMENT.md" "Guide de configuration"
check_file "QUICKSTART-ABONNEMENT.md" "Guide de démarrage rapide"
check_file "LISTE-FICHIERS.md" "Liste des fichiers"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Résumé
echo "📊 Résumé de la vérification"
echo ""
echo -e "${GREEN}✅ Succès    : $SUCCESS${NC}"
echo -e "${YELLOW}⚠️  Avertissements : $WARNINGS${NC}"
echo -e "${RED}❌ Erreurs   : $ERRORS${NC}"

echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 Parfait ! Tous les fichiers sont présents et configurés.${NC}"
    echo ""
    echo "📝 Prochaines étapes :"
    echo "1. Ouvrir le projet dans Xcode"
    echo "2. Ajouter les nouveaux fichiers au projet"
    echo "3. Configurer les Capabilities (Sign in with Apple + In-App Purchase)"
    echo "4. Tester l'application"
    echo ""
    echo "📖 Consultez QUICKSTART-ABONNEMENT.md pour plus de détails."
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Configuration partiellement complète.${NC}"
    echo "Certains éléments nécessitent une vérification manuelle."
    echo ""
    echo "📖 Consultez CONFIGURATION-ABONNEMENT.md pour les détails."
else
    echo -e "${RED}❌ Des fichiers sont manquants.${NC}"
    echo "Vérifiez que tous les fichiers ont été correctement créés."
    echo ""
    echo "📖 Consultez LISTE-FICHIERS.md pour la liste complète."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

