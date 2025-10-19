# BrightnessChat - Application iOS

Application iOS native en Swift/SwiftUI qui implémente l'interface chat RAG de Brightness.

## 📱 Aperçu

Cette application offre une interface de chat conversationnel avec RAG (Retrieval-Augmented Generation) pour iOS. Elle réplique les fonctionnalités de `simple-rag.html` dans une application mobile native.

## 🏗️ Architecture

```
BrightnessChat/
├── App/
│   ├── BrightnessChatApp.swift      # Point d'entrée
│   └── AppConfig.swift              # ⭐ Configuration JSON
├── Models/
│   ├── ChatConfig.swift             # Modèle de configuration
│   ├── Message.swift                # Modèle de message
│   └── ChatService.swift            # Service API
├── ViewModels/
│   └── ChatViewModel.swift          # Logique métier
├── Views/
│   ├── ChatView.swift               # Vue principale
│   ├── MessageRow.swift             # Ligne de message
│   ├── ComposerView.swift           # Zone de saisie
│   ├── TypingIndicator.swift        # Indicateur de frappe
│   └── ColorExtension.swift         # Design system
└── Resources/
    ├── Assets.xcassets/             # Images et icônes
    └── *.json                       # Fichiers de configuration
```

## ⚙️ Configuration

### Changer le fichier de configuration JSON

Pour modifier la configuration utilisée par l'application, éditez le fichier **`AppConfig.swift`** :

```swift
struct AppConfig {
    /// ⭐ Modifiez cette valeur pour changer le fichier de configuration
    static let defaultConfigFile = "oraldubac"  // Sans extension .json
}
```

### Configurations disponibles

Les fichiers JSON suivants sont embarqués dans l'application :

- `brightness` - Agent Brightness général
- `oraldubac` - Coach oral du Bac (TED/TEDx)
- `scenarioplanning` - Coach Scenario Planning
- `scenarioplanning2` - Scenario Planning v2
- `chat-config` - Configuration par défaut
- `bi_adaptability3` - Adaptabilité v3
- `bi_adaptability2` - Adaptabilité v2
- `bi_adaptatbility` - Adaptabilité v1

### Structure d'un fichier JSON de configuration

```json
{
  "title": "Titre de l'application",
  "logoUrl": "img/logo.png",
  "apiUrl": "https://api.example.com/chat",
  "searchUrl": "https://api.example.com/searchcontext",
  "apiKey": "votre-clé-api",
  "brain_id": "identifiant-brain",
  "model": "claude",
  "temperature": 0,
  "withHistory": true,
  "activate_source": false,
  "initialisation": "Message d'accueil initial",
  "system": "Prompt système",
  "consigne": "Consigne pour l'IA"
}
```

## 🚀 Compilation et Installation

### Prérequis

- macOS 13.0+
- Xcode 15.0+
- iOS 16.0+ (cible de déploiement)
- Swift 5.9+

### Étapes

1. Ouvrir le projet dans Xcode :
   ```bash
   open BrightnessChat/BrightnessChat.xcodeproj
   ```

2. Sélectionner un simulateur ou un appareil iOS

3. Modifier la configuration dans `AppConfig.swift` si nécessaire

4. Compiler et exécuter (⌘R)

### Dépendances

Le projet utilise Swift Package Manager pour :
- **MarkdownUI** - Rendu Markdown dans les réponses

Les dépendances sont automatiquement téléchargées lors de la première compilation.

## 🎨 Design System

L'application utilise le design system Brightness :

| Couleur    | Hex       | Utilisation           |
|------------|-----------|-----------------------|
| Background | `#0B0B0C` | Arrière-plan          |
| Panel      | `#15161A` | Panneaux et cartes    |
| Muted      | `#24262B` | Bordures              |
| Text       | `#E8E9EC` | Texte principal       |
| Accent     | `#D73C2C` | Couleur principale    |
| Subtle     | `#9AA0A6` | Texte secondaire      |

## 🔧 Fonctionnalités

### Implémentées ✅

- ✅ Chargement de configuration JSON paramétrable
- ✅ Interface chat avec historique
- ✅ Recherche de contexte RAG
- ✅ Streaming des réponses LLM
- ✅ Rendu Markdown des réponses
- ✅ Indicateur de frappe animé
- ✅ Message d'initialisation configurable
- ✅ Bouton Stop pour annuler la génération
- ✅ Design system Brightness

### Non implémentées ❌

- ❌ Liens Brightness Contact avec historique
- ❌ Affichage des sources contextuelles (blocs dépliables)

## 📝 Utilisation

1. Lancer l'application
2. Le message d'initialisation s'affiche (si configuré)
3. Taper votre question dans le champ de saisie
4. Appuyer sur "Envoyer" ou Entrée
5. L'IA recherche le contexte pertinent
6. La réponse est streamée en temps réel
7. Utiliser "Stop" pour interrompre la génération si nécessaire

## 🔐 Sécurité

- Les clés API sont stockées dans les fichiers JSON
- **Important** : Ne pas commiter les fichiers JSON avec des clés API en production
- Envisager d'utiliser un système de gestion des secrets pour les builds de production

## 📦 Distribution

### TestFlight

1. Configurer les certificats et profils dans Xcode
2. Créer une archive (Product > Archive)
3. Uploader vers App Store Connect
4. Distribuer via TestFlight

### App Store

Suivre les guidelines d'Apple pour la soumission à l'App Store.

## 🛠️ Développement

### Ajouter un nouveau fichier JSON

1. Copier le fichier `.json` dans `Resources/`
2. Ajouter le fichier au projet Xcode (Build Phases > Copy Bundle Resources)
3. Modifier `AppConfig.defaultConfigFile` pour l'utiliser

### Modifier l'interface

Les vues SwiftUI sont dans le dossier `Views/`. Chaque composant est modulaire et réutilisable.

### Debugging

- Activer les breakpoints dans ChatViewModel pour le flux de données
- Utiliser les logs dans ChatService pour les appels API
- Tester avec différents fichiers JSON pour valider la configuration

## 📄 Licence

© 2024 Brightness Institute. Tous droits réservés.

## 👥 Support

Pour toute question ou support :
- Email : contact@brightness-institute.fr
- Web : https://www.brightness-institute.fr

---

**Version** : 1.0  
**Dernière mise à jour** : Octobre 2024

