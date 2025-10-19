#!/bin/bash
#
# Script de vérification des fichiers du projet BrightnessChat
#

cd "$(dirname "$0")/BrightnessChat"

echo "🔍 Vérification des fichiers Swift..."
echo ""

files=(
  "BrightnessChat/App/BrightnessChatApp.swift"
  "BrightnessChat/App/AppConfig.swift"
  "BrightnessChat/Models/ChatConfig.swift"
  "BrightnessChat/Models/Message.swift"
  "BrightnessChat/Models/ChatService.swift"
  "BrightnessChat/ViewModels/ChatViewModel.swift"
  "BrightnessChat/Views/ChatView.swift"
  "BrightnessChat/Views/MessageRow.swift"
  "BrightnessChat/Views/ComposerView.swift"
  "BrightnessChat/Views/TypingIndicator.swift"
  "BrightnessChat/Views/ColorExtension.swift"
  "Assets.xcassets/Contents.json"
  "Assets.xcassets/AppIcon.appiconset/Contents.json"
  "BrightnessChat/Resources/brightness.json"
  "BrightnessChat/Resources/oraldubac.json"
)

all_found=true
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ MANQUANT: $file"
    all_found=false
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$all_found" = true ]; then
  echo "✅ Tous les fichiers sont présents !"
  echo ""
  echo "Si Xcode ne compile pas, le problème vient du cache."
  echo ""
  echo "Solution :"
  echo "  1. Fermer Xcode complètement (⌘Q)"
  echo "  2. Rouvrir le projet"
  echo "  3. Product > Clean Build Folder (⇧⌘K)"
  echo "  4. Product > Build (⌘B)"
else
  echo "❌ Certains fichiers manquent."
  echo ""
  echo "Veuillez vérifier l'installation du projet."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

