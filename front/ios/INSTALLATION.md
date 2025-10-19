# Installation et Configuration - BrightnessChat iOS

## 🚀 Installation Rapide

### 1. Ouvrir le projet

```bash
cd front/ios
open BrightnessChat/BrightnessChat.xcodeproj
```

### 2. Attendre le téléchargement des dépendances

Xcode va automatiquement télécharger **MarkdownUI** via Swift Package Manager.

### 3. Choisir la configuration

Ouvrir `BrightnessChat/App/AppConfig.swift` et modifier :

```swift
static let defaultConfigFile = "oraldubac"  // Modifier ici
```

**Options disponibles** :
- `"brightness"` - Agent Brightness
- `"oraldubac"` - Coach Oral du Bac
- `"scenarioplanning"` - Scenario Planning
- `"scenarioplanning2"` - Scenario Planning v2
- `"chat-config"` - Config par défaut
- `"bi_adaptability3"` - Adaptabilité v3
- `"bi_adaptability2"` - Adaptabilité v2
- `"bi_adaptatbility"` - Adaptabilité v1

### 4. Compiler et lancer

- Sélectionner un simulateur iOS (iPhone 14, iPhone 15, etc.)
- Appuyer sur ⌘R ou cliquer sur le bouton Play ▶️

## 🔧 Configuration Détaillée

### Structure d'un fichier JSON

Chaque configuration JSON doit contenir :

```json
{
  "title": "Titre affiché en haut",
  "logoUrl": "chemin/vers/logo.png",
  "apiUrl": "https://votre-api.com/chat",
  "searchUrl": "https://votre-api.com/searchcontext",
  "apiKey": "votre-clé-api",
  "brain_id": "identifiant-du-brain",
  "model": "claude",
  "temperature": 0,
  "withHistory": true,
  "activate_source": false,
  "initialisation": "Message d'accueil",
  "system": "Prompt système de l'IA",
  "consigne": "Consigne détaillée pour l'IA"
}
```

### Ajouter une nouvelle configuration

1. **Créer le fichier JSON** :
   - Placer le fichier `.json` dans `front/`
   - Copier vers `front/ios/BrightnessChat/BrightnessChat/Resources/`

2. **Ajouter au projet Xcode** :
   - Clic droit sur le dossier Resources
   - "Add Files to BrightnessChat..."
   - Sélectionner votre fichier JSON
   - Cocher "Copy items if needed"
   - Cocher "BrightnessChat" dans Targets

3. **Utiliser la nouvelle config** :
   - Modifier `AppConfig.defaultConfigFile` avec le nom du fichier (sans .json)
   - Recompiler l'application

## 🎨 Personnalisation

### Modifier les couleurs

Éditer `Views/ColorExtension.swift` :

```swift
extension Color {
    static let brightnessBackground = Color(hex: "0B0B0C")
    static let brightnessPanel = Color(hex: "15161A")
    static let brightnessAccent = Color(hex: "D73C2C")  // Couleur principale
    // ...
}
```

### Modifier l'icône

1. Créer une icône 1024x1024 px
2. Dans Xcode, ouvrir `Assets.xcassets`
3. Cliquer sur `AppIcon`
4. Glisser-déposer votre image

### Modifier le nom de l'app

Dans Xcode :
1. Sélectionner le projet `BrightnessChat`
2. Onglet "General"
3. Modifier "Display Name"

## 🐛 Résolution de Problèmes

### Erreur "Module MarkdownUI not found"

```bash
# Dans Xcode :
File > Packages > Reset Package Caches
File > Packages > Resolve Package Versions
```

### Erreur "Configuration file not found"

Vérifier que :
1. Le fichier JSON existe dans `Resources/`
2. Le nom dans `AppConfig.swift` est correct (sans .json)
3. Le fichier est bien ajouté au Target dans Xcode

### L'app ne charge pas les messages

Vérifier :
1. La clé API dans le JSON est valide
2. Les URLs `apiUrl` et `searchUrl` sont accessibles
3. Le `brain_id` existe

### Erreur de compilation Swift

```bash
# Nettoyer le build
Product > Clean Build Folder (⇧⌘K)
# Puis recompiler
Product > Build (⌘B)
```

## 📱 Tests

### Tester sur simulateur

Recommandé :
- iPhone 15 Pro (iOS 17)
- iPhone 14 (iOS 16)
- iPad Pro 12.9"

### Tester sur appareil physique

1. Connecter l'iPhone/iPad via USB
2. Dans Xcode, sélectionner l'appareil
3. "Signing & Capabilities" > Choisir votre Team
4. Compiler et lancer

**Note** : Un compte Apple Developer gratuit suffit pour les tests.

## 🔐 Sécurité pour Production

### Ne pas exposer les clés API

Pour une app en production :

1. **Supprimer les clés des JSON** :
   ```json
   {
     "apiKey": ""
   }
   ```

2. **Utiliser un système de secrets** :
   - Keychain
   - Variables d'environnement
   - Backend proxy qui gère les clés

3. **Fichier de configuration externe** :
   - Télécharger la config depuis un serveur sécurisé
   - Chiffrer les données sensibles

## 📊 Performance

### Optimisations

- Les messages sont chargés de manière lazy (LazyVStack)
- Le streaming réduit le temps d'attente perçu
- Les images de logo sont mises en cache automatiquement

### Limites

- Historique limité par la mémoire
- Pas de persistance des conversations (à ajouter si besoin)

## 🔄 Mises à Jour

### Changer de configuration sans recompiler

**Actuellement non supporté** - nécessite recompilation.

Pour l'implémenter :
1. Ajouter un menu de sélection dans l'app
2. Stocker le choix dans UserDefaults
3. Recharger la config au lancement

## 📚 Ressources

- [Documentation Swift](https://swift.org/documentation/)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [MarkdownUI](https://github.com/gonzalezreal/swift-markdown-ui)
- [Brightness Institute](https://www.brightness-institute.fr)

---

**Support** : contact@brightness-institute.fr

