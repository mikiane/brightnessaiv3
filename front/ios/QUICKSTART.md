# 🚀 Guide de Démarrage Rapide - BrightnessChat iOS

## ✅ Installation en 3 minutes

### 1️⃣ Ouvrir le projet
```bash
cd front/ios
open BrightnessChat/BrightnessChat.xcodeproj
```

### 2️⃣ Choisir la configuration
Éditer `BrightnessChat/App/AppConfig.swift` :
```swift
static let defaultConfigFile = "oraldubac"  // ⭐ Modifier ici
```

### 3️⃣ Lancer l'app
- Sélectionner un simulateur (iPhone 15)
- Appuyer sur ▶️ ou ⌘R

**C'est tout !** L'app va :
1. Télécharger MarkdownUI automatiquement
2. Charger la configuration `oraldubac.json`
3. Afficher le message d'accueil
4. Être prête à discuter

---

## 📋 Configurations Disponibles

| Nom du fichier       | Description                          |
|---------------------|--------------------------------------|
| `brightness`        | Agent Brightness général             |
| `oraldubac`         | Coach oral du Bac (TED/TEDx)         |
| `scenarioplanning`  | Coach Scenario Planning              |
| `scenarioplanning2` | Scenario Planning v2                 |
| `chat-config`       | Configuration par défaut             |
| `bi_adaptability3`  | Adaptabilité v3                      |

---

## 🔧 Personnalisation Rapide

### Changer le titre
Dans le fichier JSON :
```json
"title": "Mon Super Coach"
```

### Changer le message d'accueil
Dans le fichier JSON :
```json
"initialisation": "Bonjour ! Comment puis-je vous aider ?"
```

### Changer la couleur principale
Dans `Views/ColorExtension.swift` :
```swift
static let brightnessAccent = Color(hex: "D73C2C")  // Rouge Brightness
```

---

## 📱 Tests Recommandés

### Sur Simulateur
```
iPhone 15 Pro (iOS 17)    ← Recommandé
iPhone 14 (iOS 16)        ← Minimum supporté
iPad Pro 12.9"            ← Tablette
```

### Sur Appareil Physique
1. Connecter l'iPhone via USB
2. Sélectionner l'appareil dans Xcode
3. "Signing & Capabilities" → Choisir votre Apple ID
4. Build & Run ▶️

---

## ❓ Questions Fréquentes

### L'app ne compile pas ?
```bash
# Nettoyer le projet
Product > Clean Build Folder (⇧⌘K)

# Réinitialiser les packages
File > Packages > Reset Package Caches
```

### Erreur "Configuration file not found" ?
Vérifier que :
- Le nom dans `AppConfig.swift` est **sans** extension `.json`
- Le fichier existe dans `Resources/`
- Le fichier est coché dans le Target Xcode

### L'IA ne répond pas ?
Vérifier dans le JSON :
- `apiUrl` est accessible
- `searchUrl` est accessible  
- `apiKey` est valide
- `brain_id` existe

---

## 📚 Documentation Complète

- **README.md** - Vue d'ensemble et architecture
- **INSTALLATION.md** - Guide d'installation détaillé
- **TECHNICAL.md** - Documentation technique avancée
- **Ce fichier** - Guide de démarrage rapide

---

## 🎯 Prochaines Étapes

### Pour Production
1. Remplacer les clés API par un système sécurisé
2. Ajouter une icône personnalisée (1024x1024)
3. Configurer les certificats de distribution
4. Tester sur plusieurs appareils
5. Créer une archive pour TestFlight

### Améliorations Possibles
- [ ] Persistance des conversations (CoreData)
- [ ] Sélection de config dans l'app (sans recompilation)
- [ ] Mode hors-ligne avec cache
- [ ] Support du mode sombre/clair
- [ ] Export des conversations (PDF, texte)
- [ ] Partage de messages
- [ ] Synthèse vocale des réponses
- [ ] Reconnaissance vocale pour les questions

---

## 💬 Support

**Email** : contact@brightness-institute.fr  
**Web** : https://www.brightness-institute.fr

---

**Bon développement !** 🚀

