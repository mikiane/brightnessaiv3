# Guide de Sécurisation des API BrightnessAI v3

## 🔒 Système de Sécurité Implémenté

### Deux méthodes d'authentification :

1. **Domaine autorisé** : Requêtes depuis `*.brightness.agency`
2. **Clé API** : Pour tous les autres domaines avec la clé `FRONT_BRIGHTNESS_KEY`

## 📋 Configuration

### 1. Ajouter la clé secrète dans `.env`

```bash
# Générer une clé sécurisée
openssl rand -hex 32

# Ajouter dans .env
FRONT_BRIGHTNESS_KEY=votre-clé-générée-ici
```

### 2. Protéger les routes API

Pour chaque route que vous voulez protéger, ajoutez `@require_auth` :

```python
@app.route('/votre-route', methods=['POST'])
@require_auth  # Ajouter cette ligne
def votre_fonction():
    ...
```

## 🔧 Utilisation côté Client

### Depuis Bubble (brightness.agency)
Aucun changement nécessaire - l'authentification est automatique via le domaine.

### Depuis un autre domaine

#### Option 1 : Header Authorization
```javascript
fetch('https://api.example.com/stream_chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_FRONT_BRIGHTNESS_KEY'
    },
    body: JSON.stringify(data)
})
```

#### Option 2 : Header X-API-Key
```javascript
fetch('https://api.example.com/stream_chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'YOUR_FRONT_BRIGHTNESS_KEY'
    },
    body: JSON.stringify(data)
})
```

#### Option 3 : Dans le body JSON
```javascript
fetch('https://api.example.com/stream_chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        ...data,
        api_key: 'YOUR_FRONT_BRIGHTNESS_KEY'
    })
})
```

## ✅ Routes Actuellement Protégées

### streaming_api.py
- ✅ `/stream_chat` - Chat en streaming
- ✅ `/stream_chat_temp` - Chat avec température
- ✅ `/chat` - Alias pour compatibilité

### transformers_api.py (À FAIRE)
- ⚠️ `/sumup` - Résumé de documents
- ⚠️ `/transform` - Transformation de texte
- ⚠️ `/podcast` - Génération de podcast
- ⚠️ `/whisper` - Transcription audio

### alter_brain_api.py (À FAIRE)
- ⚠️ `/buildindex` - Construction d'index
- ⚠️ `/searchcontext` - Recherche contextuelle
- ⚠️ `/streamtasks` - Exécution de tâches

## 🛡️ Headers de Sécurité Ajoutés

Toutes les réponses incluent maintenant :
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 📝 Pour Activer la Protection Complète

Ajoutez `@require_auth` aux routes restantes dans :
- `api/transformers_api.py`
- `api/alter_brain_api.py`

Exemple :
```python
@app.route('/sumup', methods=['POST'])
@require_auth  # Ajouter cette ligne
def sumup():
    ...
```

## 🧪 Test de la Sécurité

```bash
# Test sans authentification (devrait retourner 403)
curl -X POST http://localhost:8000/stream_chat \
  -H "Content-Type: application/json" \
  -d '{"consigne":"test","texte":"test"}'

# Test avec clé API (devrait fonctionner)
curl -X POST http://localhost:8000/stream_chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_FRONT_BRIGHTNESS_KEY" \
  -d '{"consigne":"test","texte":"test"}'
```

## ⚠️ Important

1. **Ne jamais exposer** `FRONT_BRIGHTNESS_KEY` dans le code frontend public
2. **Utiliser HTTPS** en production pour protéger la clé en transit
3. **Rotation régulière** de la clé (tous les 3-6 mois)
4. **Monitoring** des logs pour détecter les tentatives non autorisées
