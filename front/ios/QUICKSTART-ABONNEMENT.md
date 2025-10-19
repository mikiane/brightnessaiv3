# Guide de Démarrage Rapide - Abonnement

## ✅ Ce qui a été fait

Votre application iOS dispose maintenant de :

1. **Sign in with Apple** 🔐
   - Authentification sécurisée avec le compte Apple
   - Pas besoin de créer un compte manuel

2. **5 requêtes gratuites** 🎁
   - Les utilisateurs peuvent tester l'app gratuitement
   - Compteur visible en bas de l'écran

3. **Abonnement mensuel à 15€** 💳
   - Requêtes illimitées avec l'abonnement
   - Paiement sécurisé via l'App Store
   - Annulation facile à tout moment

4. **Gestion du compte** ⚙️
   - Paramètres accessibles depuis l'icône engrenage
   - Restauration des achats
   - Déconnexion

---

## 🚀 Prochaines étapes (dans l'ordre)

### 1. Ouvrir le projet dans Xcode

```bash
cd /Users/michel/Dropbox\ \(Compte\ personnel\)/1-DEVELOPPEMENTS/Git/brightnessaiv3/front/ios
open BrightnessChat/BrightnessChat.xcodeproj
```

### 2. Ajouter les nouveaux fichiers au projet

**Dans Xcode** :

1. **Clic droit** sur le dossier `Models` → **Add Files to "BrightnessChat"**
   - Sélectionner :
     - `AuthenticationManager.swift`
     - `SubscriptionManager.swift`
     - `UsageManager.swift`
   - ✅ Cocher "Copy items if needed"
   - ✅ Cocher le target "BrightnessChat"

2. **Clic droit** sur le dossier `Views` → **Add Files to "BrightnessChat"**
   - Sélectionner :
     - `LoginView.swift`
     - `SubscriptionView.swift`
     - `SettingsView.swift`
   - ✅ Cocher "Copy items if needed"
   - ✅ Cocher le target "BrightnessChat"

3. **Ajouter le fichier StoreKit** au projet racine :
   - Clic droit sur "BrightnessChat" (racine) → **Add Files to "BrightnessChat"**
   - Sélectionner : `BrightnessStore.storekit`

### 3. Configurer les Capabilities

1. Sélectionner le **target "BrightnessChat"** dans le navigateur
2. Onglet **"Signing & Capabilities"**
3. Cliquer sur **"+ Capability"**
4. Ajouter :
   - ✅ **Sign in with Apple**
   - ✅ **In-App Purchase**

### 4. Activer StoreKit Configuration pour les tests

1. Menu **Product** → **Scheme** → **Edit Scheme...**
2. Onglet **"Run"** → **Options**
3. **StoreKit Configuration** : Sélectionner `BrightnessStore.storekit`
4. Cliquer sur **"Close"**

### 5. Compiler et tester

```bash
# Depuis Xcode : Cmd + R
```

**Vérifier que :**
- ✅ L'écran de login s'affiche au démarrage
- ✅ Le bouton "Sign in with Apple" fonctionne
- ✅ Le chat s'affiche après connexion
- ✅ Le compteur de requêtes s'affiche en bas
- ✅ Après 5 requêtes, l'écran d'abonnement apparaît
- ✅ Le bouton "S'abonner" ouvre le dialogue de paiement

---

## 🧪 Mode Test (Simulateur)

En mode simulateur avec StoreKit Configuration :
- ✅ **Aucun paiement réel** n'est effectué
- ✅ L'abonnement se valide instantanément
- ✅ Vous pouvez gérer les transactions : **Debug** → **StoreKit** → **Manage Transactions**

### Réinitialiser le compteur de requêtes

En mode Debug, l'app affiche un bouton dans les **Paramètres** :
- Ouvrir les Paramètres (icône engrenage)
- Cliquer sur **"Réinitialiser le compteur (Debug)"**
- Le compteur repasse à 0

---

## 📱 Mode Test (iPhone réel avec Sandbox)

Pour tester sur un iPhone réel **sans payer** :

### 1. Créer un compte Sandbox dans App Store Connect

1. Aller sur https://appstoreconnect.apple.com
2. **Users and Access** → **Sandbox Testers**
3. Créer un nouveau testeur :
   - Email : `testbrightness@example.com` (email fictif)
   - Mot de passe : Un mot de passe fort
   - Pays : France

### 2. Configurer l'iPhone

1. **Réglages** → **App Store**
2. **Se déconnecter** du compte App Store normal (en haut)
3. **NE PAS se connecter** avec le compte Sandbox maintenant

### 3. Installer et tester

1. Installer l'app via Xcode (Cmd + R)
2. Lancer l'app sur l'iPhone
3. Faire 5 requêtes
4. Lors de l'achat, iOS demandera un compte App Store
5. **Se connecter avec le compte Sandbox** : `testbrightness@example.com`
6. L'abonnement se valide **sans paiement réel**

---

## 🏪 Configuration App Store Connect (Avant publication)

⚠️ **Obligatoire avant de publier l'app**

Voir le guide complet : **[CONFIGURATION-ABONNEMENT.md](./CONFIGURATION-ABONNEMENT.md)**

**Résumé des étapes critiques :**

1. Créer l'app dans App Store Connect
2. Créer le produit d'abonnement :
   - **Product ID** : `com.brightness.chat.monthly`
   - **Prix** : 14,99 € ou 15,00 €
   - **Durée** : 1 mois
3. Activer Sign in with Apple dans le Developer Portal
4. Soumettre l'app pour révision

---

## 📋 Checklist rapide

Avant de tester :
- [ ] Fichiers ajoutés au projet Xcode
- [ ] Capabilities ajoutées (Sign in with Apple + In-App Purchase)
- [ ] StoreKit Configuration activée dans le Scheme
- [ ] L'app compile sans erreur (Cmd + B)

Avant de publier :
- [ ] Abonnement créé dans App Store Connect
- [ ] Product ID correspond : `com.brightness.chat.monthly`
- [ ] Tests réalisés avec compte Sandbox
- [ ] Screenshots préparés
- [ ] Privacy Policy ajoutée (si nécessaire)

---

## 🔧 Modification du prix

Si vous voulez changer le prix (actuellement 15€/mois) :

1. **Dans App Store Connect** :
   - Modifier le prix du produit d'abonnement

2. **Dans `BrightnessStore.storekit`** (pour les tests) :
   - Ligne 50 : Changer `"displayPrice" : "14.99"`

⚠️ Le prix dans le code est **récupéré automatiquement** depuis l'App Store, pas besoin de le modifier dans Swift.

---

## 📖 Liens utiles

- **Guide complet** : [CONFIGURATION-ABONNEMENT.md](./CONFIGURATION-ABONNEMENT.md)
- **Installation iPhone** : [INSTALL-IPHONE.md](./INSTALL-IPHONE.md)
- **App Store Connect** : https://appstoreconnect.apple.com
- **Apple Developer** : https://developer.apple.com

---

## 🆘 Problèmes courants

### L'écran de login ne s'affiche pas

**Solution** :
- Vérifier que `LoginView.swift` est bien ajouté au projet
- Vérifier que `AuthenticationManager.swift` est présent

### "Product ID not found" lors de l'achat

**Solution** :
- En mode simulateur : Vérifier que `BrightnessStore.storekit` est activé dans le Scheme
- En mode iPhone réel : Créer le produit dans App Store Connect (attendre 2-3h après création)

### Le compteur ne s'affiche pas

**Solution** :
- Vérifier que `UsageManager.swift` est bien ajouté
- Vérifier que les modifications de `ComposerView.swift` sont présentes

### Sign in with Apple ne fonctionne pas

**Solution** :
- Vérifier que la capability "Sign in with Apple" est ajoutée
- Sur simulateur : Se connecter avec un Apple ID dans Réglages → Apple ID

---

## 🎯 Flux de l'application

```
1. Démarrage
   ↓
2. Écran de login → Sign in with Apple
   ↓
3. Chat principal (compteur visible en bas)
   ↓
4. Requête 1, 2, 3, 4, 5 → OK
   ↓
5. Requête 6+ → Écran d'abonnement s'affiche
   ↓
6. Utilisateur s'abonne (ou annule)
   ↓
7. Si abonné → Requêtes illimitées ✅
   Si non abonné → Blocage à 5 requêtes 🚫
```

---

**Vous êtes prêt !** 🚀

Si vous avez des questions, consultez le guide complet [CONFIGURATION-ABONNEMENT.md](./CONFIGURATION-ABONNEMENT.md).

