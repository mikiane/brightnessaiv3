#!/bin/bash
#
# Script de réinitialisation complète du cache Xcode
#

echo "🧹 Nettoyage complet du cache Xcode..."
echo ""

# 1. Supprimer DerivedData
echo "1️⃣ Suppression de DerivedData..."
rm -rf ~/Library/Developer/Xcode/DerivedData/* 2>/dev/null
echo "   ✅ DerivedData nettoyé"

# 2. Supprimer les données utilisateur du projet
echo "2️⃣ Suppression des données utilisateur du projet..."
cd "/Users/michel/Dropbox (Compte personnel)/1-DEVELOPPEMENTS/Git/brightnessaiv3/front/ios/BrightnessChat"
rm -rf BrightnessChat.xcodeproj/xcuserdata 2>/dev/null
rm -rf BrightnessChat.xcodeproj/project.xcworkspace/xcuserdata 2>/dev/null
echo "   ✅ Données utilisateur supprimées"

# 3. Vérifier la structure du projet
echo "3️⃣ Vérification de la structure..."
if [ -d "BrightnessChat/Assets.xcassets/AppIcon.appiconset" ]; then
    echo "   ✅ Assets.xcassets présent"
    if [ -f "BrightnessChat/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png" ]; then
        echo "   ✅ AppIcon-1024.png présent"
    else
        echo "   ⚠️  AppIcon-1024.png manquant"
    fi
else
    echo "   ❌ Assets.xcassets manquant"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Nettoyage terminé !"
echo ""
echo "📝 Prochaines étapes :"
echo "  1. Si Xcode est ouvert : le fermer complètement (⌘Q)"
echo "  2. Rouvrir le projet :"
echo "     open BrightnessChat.xcodeproj"
echo "  3. Dans Xcode :"
echo "     - Product > Clean Build Folder (⇧⌘K)"
echo "     - Product > Build (⌘B)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

