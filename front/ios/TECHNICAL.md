# Documentation Technique - BrightnessChat iOS

## 🏗️ Architecture Technique

### Pattern MVVM

L'application suit le pattern **Model-View-ViewModel** :

```
┌─────────────┐
│    View     │ ← SwiftUI (ChatView, MessageRow, etc.)
└──────┬──────┘
       │ Binding (@Published)
┌──────▼──────┐
│  ViewModel  │ ← ChatViewModel (logique métier)
└──────┬──────┘
       │
┌──────▼──────┐
│   Model     │ ← ChatConfig, Message
│  + Service  │ ← ChatService (API)
└─────────────┘
```

### Flux de données

```
User Input (TextField)
  ↓
ChatViewModel.sendMessage()
  ↓
ChatService.fetchContext() → API RAG
  ↓
ChatService.sendToLLM() → API Streaming
  ↓
AsyncThrowingStream<String>
  ↓
ViewModel update @Published
  ↓
SwiftUI Auto-Refresh
```

## 📦 Composants Principaux

### 1. BrightnessChatApp.swift

Point d'entrée de l'application.

```swift
@main
struct BrightnessChatApp: App {
    var body: some Scene {
        WindowGroup {
            ChatView()
        }
    }
}
```

### 2. AppConfig.swift

**Rôle** : Définir la configuration JSON à charger au démarrage.

```swift
struct AppConfig {
    static let defaultConfigFile = "oraldubac"
}
```

**Modification** : C'est le seul fichier à modifier pour changer de configuration.

### 3. ChatConfig.swift

**Rôle** : Modèle Codable pour les fichiers JSON.

**Champs importants** :
- `apiUrl` : Endpoint du LLM
- `searchUrl` : Endpoint de recherche RAG
- `brain_id` : Identifiant du brain de connaissance
- `withHistory` : Active/désactive l'historique conversationnel
- `initialisation` : Message d'accueil initial

**Méthode clé** :
```swift
static func load(from filename: String) throws -> ChatConfig
```

### 4. Message.swift

**Rôle** : Représenter un message dans le chat.

```swift
struct Message: Identifiable {
    let id: UUID
    let role: MessageRole  // .user, .assistant, .system
    var content: String
    let timestamp: Date
}
```

### 5. ChatService.swift

**Rôle** : Gestion des appels API.

**Méthodes principales** :

#### fetchContext()
```swift
func fetchContext(for query: String) async throws -> String
```
- Envoie une requête POST au `searchUrl`
- Format : `multipart/form-data`
- Paramètres : `request`, `brain_id`, `model`
- Retourne : Contexte RAG trouvé

#### sendToLLM()
```swift
func sendToLLM(question: String, context: String, history: [Message]) 
    async throws -> AsyncThrowingStream<String, Error>
```
- Envoie la question + contexte au `apiUrl`
- Format : JSON
- Streaming : via `URLSession.bytes(for:)`
- Retourne : Stream de caractères

#### buildConsigne()
```swift
private func buildConsigne(baseConsigne: String, history: [Message], context: String) -> String
```
- Construit la consigne finale pour le LLM
- Ajoute l'historique (4 derniers messages)
- Ajoute le contexte RAG

### 6. ChatViewModel.swift

**Rôle** : Logique métier et état de l'application.

**État @Published** :
```swift
@Published var messages: [Message] = []
@Published var config: ChatConfig?
@Published var isLoading = false
@Published var isSending = false
@Published var errorMessage: String?
@Published var statusText = ""
```

**Méthodes clés** :

#### loadConfiguration()
```swift
func loadConfiguration()
```
- Charge le JSON depuis `AppConfig.defaultConfigFile`
- Initialise le `ChatService`
- Ajoute le message d'initialisation si présent

#### sendMessage()
```swift
func sendMessage(_ text: String)
```
1. Ajoute le message utilisateur à l'historique
2. Crée un message assistant vide
3. Lance une Task asynchrone :
   - Récupère le contexte via `fetchContext()`
   - Envoie au LLM via `sendToLLM()`
   - Stream la réponse caractère par caractère
   - Met à jour le message en temps réel

#### stopGeneration()
```swift
func stopGeneration()
```
- Annule la Task en cours
- Réinitialise l'état UI

### 7. ChatView.swift

**Rôle** : Vue principale conteneur.

**Structure** :
```swift
VStack {
    Header (logo + titre)
    ScrollView {
        Messages (LazyVStack)
        TypingIndicator (conditionnel)
    }
    ComposerView (input + boutons)
}
```

**Fonctionnalités** :
- Auto-scroll vers le bas lors de nouveaux messages
- Gestion des alertes d'erreur
- Focus automatique sur le TextField

### 8. MessageRow.swift

**Rôle** : Affichage d'un message (user ou assistant).

**Composants** :
- Avatar circulaire (couleur selon le rôle)
- Contenu :
  - User : Text simple
  - Assistant : Markdown avec MarkdownUI

**Thème Markdown personnalisé** :
```swift
extension Theme {
    static let brightness = Theme()
        .text { ForegroundColor(.brightnessText) }
        .code { BackgroundColor(Color(hex: "0f1115")) }
        .link { ForegroundColor(.brightnessAccent) }
}
```

### 9. ComposerView.swift

**Rôle** : Zone de saisie et boutons d'action.

**Composants** :
- TextField multiline (3-6 lignes)
- Bouton "Stop" (conditionnel si `isSending`)
- Bouton "Envoyer" (gradient, désactivé si vide)
- Label de statut

**Interaction** :
- Entrée = envoyer (sauf si Shift+Entrée)
- Désactivation pendant l'envoi

### 10. TypingIndicator.swift

**Rôle** : Animation de "frappe" (3 points).

**Implémentation** :
```swift
3 cercles animés avec :
- Opacité : 0.2 ↔ 1.0
- Délai : 0s, 0.2s, 0.4s
- Durée : 0.6s
- Repeat forever
```

### 11. ColorExtension.swift

**Rôle** : Design system Brightness.

**Couleurs définies** :
```swift
Color.brightnessBackground  // #0B0B0C
Color.brightnessPanel       // #15161A
Color.brightnessMuted       // #24262B
Color.brightnessText        // #E8E9EC
Color.brightnessAccent      // #D73C2C
Color.brightnessSubtle      // #9AA0A6
```

**Helper** :
```swift
init(hex: String)  // Créer une Color depuis hex
```

## 🔄 Cycle de Vie d'une Question

```
1. User tape "Quelle est la méthode Brightness ?"
   ↓
2. TextField → Binding → inputText
   ↓
3. Bouton "Envoyer" → ChatViewModel.sendMessage()
   ↓
4. Ajout du message user dans messages[]
   ↓
5. Création d'un message assistant vide
   ↓
6. ChatService.fetchContext("Quelle est la méthode Brightness ?")
   ↓
7. POST vers searchUrl avec brain_id
   ↓
8. Réception du contexte RAG
   ↓
9. Construction de la consigne :
   - system
   - consigne de base
   - historique (4 derniers messages)
   - contexte RAG
   ↓
10. ChatService.sendToLLM(question, context, history)
   ↓
11. POST vers apiUrl avec payload JSON
   ↓
12. Streaming de la réponse :
    "La" → "La méthode" → "La méthode Brightness"...
   ↓
13. Pour chaque chunk :
    - Ajout au contenu accumulé
    - Update du message assistant
    - SwiftUI rafraîchit automatiquement
    - Auto-scroll si en bas
   ↓
14. Fin du stream
   ↓
15. Message complet affiché
   ↓
16. Ajout à l'historique pour le contexte suivant
```

## 🧪 Tests et Debugging

### Logs utiles

Ajouter dans `ChatService.swift` :
```swift
print("🔍 Searching context for: \(query)")
print("📡 API Response: \(data)")
print("📝 Built consigne: \(consigne)")
```

### Breakpoints recommandés

- `ChatViewModel.sendMessage()` : Vérifier le flow
- `ChatService.fetchContext()` : Inspecter la réponse RAG
- `ChatService.sendToLLM()` : Vérifier le payload

### Simuler une erreur

Dans `ChatService.swift`, forcer un throw :
```swift
throw ChatError.searchFailed
```

## 🚀 Optimisations Possibles

### 1. Cache des contextes
```swift
class ContextCache {
    private var cache: [String: String] = [:]
    
    func get(_ query: String) -> String? {
        cache[query]
    }
    
    func set(_ query: String, context: String) {
        cache[query] = context
    }
}
```

### 2. Persistance avec CoreData
- Sauvegarder les conversations
- Reprendre une session

### 3. Pagination des messages
- Charger les messages par batch
- Améliorer les performances avec beaucoup de messages

### 4. Retry automatique
```swift
func fetchContextWithRetry(for query: String, maxRetries: Int = 3) async throws -> String {
    for attempt in 1...maxRetries {
        do {
            return try await fetchContext(for: query)
        } catch {
            if attempt == maxRetries { throw error }
            try await Task.sleep(nanoseconds: UInt64(attempt) * 1_000_000_000)
        }
    }
    throw ChatError.searchFailed
}
```

### 5. Configuration distante
- Télécharger le JSON depuis un serveur
- Mise à jour sans recompilation

## 📊 Métriques de Performance

### Temps de réponse typiques
- Chargement config : < 50ms
- Recherche contexte : 200-500ms
- Première réponse LLM : 500-1000ms
- Streaming complet : 2-5s (selon longueur)

### Consommation mémoire
- Base : ~50 MB
- Avec 100 messages : ~70 MB
- Images en cache : +variable

### Réseau
- Recherche contexte : ~5-10 KB
- Réponse LLM : ~2-20 KB (streaming)

## 🔒 Sécurité

### Points d'attention
1. **API Keys** : Stocker dans Keychain (pas dans le JSON)
2. **HTTPS** : Toujours utiliser HTTPS pour les APIs
3. **Validation** : Valider les réponses JSON
4. **Timeout** : Ajouter des timeouts aux requêtes
5. **Rate limiting** : Implémenter côté serveur

### Code de sécurité recommandé
```swift
// Timeout de 30 secondes
var request = URLRequest(url: url)
request.timeoutInterval = 30

// Validation SSL
URLSession(configuration: .default, delegate: sslPinningDelegate, delegateQueue: nil)
```

## 📚 Dépendances

### MarkdownUI (2.0+)
- **Repo** : https://github.com/gonzalezreal/swift-markdown-ui
- **Licence** : MIT
- **Usage** : Rendu Markdown dans MessageRow
- **Alternative** : SwiftUI Text avec AttributedString

### URLSession (native)
- Gestion des requêtes HTTP
- Streaming via `.bytes(for:)`

### SwiftUI (native)
- Framework UI déclaratif
- Binding automatique

## 🔧 Configuration Xcode

### Build Settings recommandés
```
IPHONEOS_DEPLOYMENT_TARGET = 16.0
SWIFT_VERSION = 5.0
ENABLE_PREVIEWS = YES
```

### Info.plist
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>
```

---

**Version** : 1.0  
**Dernière mise à jour** : Octobre 2024

