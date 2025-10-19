# Configuration de l'Abonnement et Sign in with Apple

Ce guide explique comment configurer votre application iOS pour utiliser Sign in with Apple et les achats in-app (abonnement mensuel à 15€).

## Table des matières
1. [Configuration Xcode](#1-configuration-xcode)
2. [Configuration App Store Connect](#2-configuration-app-store-connect)
3. [Configuration Sign in with Apple](#3-configuration-sign-in-with-apple)
4. [Configuration StoreKit pour les tests](#4-configuration-storekit-pour-les-tests)
5. [Tests de l'abonnement](#5-tests-de-labonnement)
6. [Publication](#6-publication)

---

## 1. Configuration Xcode

### 1.1 Ajouter les Capabilities au projet

1. **Ouvrir le projet dans Xcode**
   ```bash
   cd front/ios
   open BrightnessChat/BrightnessChat.xcodeproj
   ```

2. **Sélectionner le target "BrightnessChat"** dans le navigateur de projet

3. **Aller dans l'onglet "Signing & Capabilities"**

4. **Cliquer sur "+ Capability"** et ajouter :
   - **Sign in with Apple**
   - **In-App Purchase**

5. **Vérifier que votre Team est bien sélectionné**
   - Dans "Signing", choisissez votre équipe de développement Apple

### 1.2 Configurer le Bundle Identifier

Le Bundle ID doit correspondre à celui configuré dans App Store Connect :
- Par exemple : `com.brightness.chat`

### 1.3 Ajouter les fichiers au projet

Tous les nouveaux fichiers ont été créés. Maintenant, **ajoutez-les au projet Xcode** :

1. Dans Xcode, clic droit sur le dossier `Models` → Add Files to "BrightnessChat"
   - Sélectionner : `AuthenticationManager.swift`, `SubscriptionManager.swift`, `UsageManager.swift`

2. Dans Xcode, clic droit sur le dossier `Views` → Add Files to "BrightnessChat"
   - Sélectionner : `LoginView.swift`, `SubscriptionView.swift`, `SettingsView.swift`

3. **Vérifier que les fichiers sont bien ajoutés** dans le navigateur de projet

---

## 2. Configuration App Store Connect

### 2.1 Créer l'App

1. **Aller sur App Store Connect** : https://appstoreconnect.apple.com

2. **Créer une nouvelle app** :
   - Cliquer sur "My Apps" → "+" → "New App"
   - Platform : iOS
   - Name : Brightness Chat (ou votre nom)
   - Primary Language : French
   - Bundle ID : Sélectionner celui de votre app (ex: com.brightness.chat)
   - SKU : Un identifiant unique (ex: brightness-chat-001)
   - User Access : Full Access

### 2.2 Configurer l'abonnement

1. **Aller dans "Features" → "In-App Purchases"**

2. **Créer un nouveau produit d'abonnement** :
   - Cliquer sur "+" → "Auto-Renewable Subscription"

3. **Créer un Subscription Group** :
   - Reference Name : "Brightness Premium"
   - App Name : "Premium"

4. **Configurer le produit d'abonnement** :
   - **Product ID** : `com.brightness.chat.monthly`
     ⚠️ **IMPORTANT** : Ce Product ID doit correspondre à celui dans `SubscriptionManager.swift` ligne 18
   
   - **Reference Name** : Brightness Chat Premium Monthly
   
   - **Subscription Duration** : 1 month
   
   - **Subscription Prices** :
     - Cliquer sur "Add Pricing"
     - Pays : France
     - Prix : 14,99 € (ou 15,00 € selon votre préférence)
     - Ajouter d'autres pays si nécessaire

5. **Localisation française** :
   - Subscription Display Name : Premium
   - Description : Accès illimité à toutes les fonctionnalités de Brightness Chat avec requêtes illimitées.

6. **Review Information** :
   - Remplir les informations requises pour la révision Apple
   - Screenshot (optionnel mais recommandé)

7. **Cliquer sur "Save"**

### 2.3 Configurer les Sandbox Testers

1. **Aller dans "Users and Access" → "Sandbox Testers"**

2. **Créer un nouveau testeur** :
   - Cliquer sur "+"
   - First Name : Test
   - Last Name : User
   - Email : Un email qui n'existe PAS dans votre Apple ID (ex: testbrightness@example.com)
   - Password : Un mot de passe fort
   - Country/Region : France
   - App Store Territory : France

3. **Sauvegarder**

---

## 3. Configuration Sign in with Apple

### 3.1 Dans Apple Developer Portal

1. **Aller sur** : https://developer.apple.com/account

2. **Certificates, Identifiers & Profiles** → **Identifiers**

3. **Sélectionner votre App ID** (ex: com.brightness.chat)

4. **Cocher "Sign in with Apple"**
   - Cliquer sur "Edit"
   - Configurer comme Primary App ID (si c'est votre première app)
   - Sauvegarder

5. **Régénérer le Provisioning Profile si nécessaire**

### 3.2 Dans Xcode

Les capabilities ont déjà été ajoutées à l'étape 1.1, mais vérifiez :
- ✅ Sign in with Apple doit être présent dans "Signing & Capabilities"

---

## 4. Configuration StoreKit pour les tests

Pour tester les achats in-app **sans payer réellement**, utilisez le fichier StoreKit Configuration.

### 4.1 Créer un fichier StoreKit Configuration

1. **Dans Xcode** : File → New → File

2. **Chercher "StoreKit"** → Sélectionner "StoreKit Configuration File"

3. **Nom du fichier** : `BrightnessStore.storekit`

4. **Ajouter un produit d'abonnement** :
   - Cliquer sur "+" en bas à gauche
   - Choisir "Add Auto-Renewable Subscription"

5. **Configurer le produit** :
   - **Reference Name** : Premium Monthly
   - **Product ID** : `com.brightness.chat.monthly` (⚠️ identique à App Store Connect)
   - **Price** : 14.99
   - **Locale** : fr_FR (French - France)
   - **Subscription Duration** : 1 Month
   - **Description** : Requêtes illimitées
   - **Display Name** : Premium

6. **Sauvegarder le fichier**

### 4.2 Activer le StoreKit Configuration

1. **Sélectionner le scheme** : Product → Scheme → Edit Scheme

2. **Onglet "Run"** → **Options**

3. **StoreKit Configuration** : Sélectionner `BrightnessStore.storekit`

4. **Cliquer sur "Close"**

---

## 5. Tests de l'abonnement

### 5.1 Tester en mode simulateur (avec StoreKit Configuration)

1. **Lancer l'app dans le simulateur**
   ```bash
   # Depuis Xcode : Cmd + R
   ```

2. **Vérifier le flux** :
   - ✅ L'écran de login apparaît
   - ✅ Sign in with Apple fonctionne
   - ✅ Le compteur de requêtes s'affiche
   - ✅ Après 5 requêtes, la vue d'abonnement s'affiche
   - ✅ Le bouton "S'abonner" fonctionne
   - ✅ L'abonnement se valide

3. **Gérer les transactions de test** :
   - Dans Xcode : Debug → StoreKit → Manage Transactions
   - Vous pouvez voir/supprimer/modifier les transactions

### 5.2 Tester sur un appareil réel (avec Sandbox)

1. **Se déconnecter de l'App Store** sur l'iPhone :
   - Réglages → App Store → Se déconnecter (en haut)

2. **NE PAS se connecter** avec le compte Sandbox avant de lancer l'app

3. **Installer l'app** sur l'iPhone via Xcode

4. **Lancer l'app**

5. **Lors de l'achat**, iOS demandera de se connecter :
   - Utiliser le compte **Sandbox Tester** créé à l'étape 2.3
   - Email : testbrightness@example.com
   - Password : Le mot de passe créé

6. **Vérifier** :
   - ✅ L'achat se fait sans paiement réel
   - ✅ L'abonnement s'active
   - ✅ Les requêtes deviennent illimitées

7. **Annuler l'abonnement** (pour tester) :
   - Réglages → App Store → Sandbox Account → Gérer

---

## 6. Publication

### 6.1 Préparer la soumission

1. **Dans App Store Connect**, aller dans votre app

2. **Onglet "App Store"**

3. **Remplir toutes les informations** :
   - Screenshots (obligatoire pour iPhone 6.7" et 6.5")
   - App Preview (optionnel)
   - Description
   - Keywords
   - Support URL
   - Marketing URL (optionnel)
   - Privacy Policy URL (obligatoire si vous collectez des données)

4. **Informations sur l'abonnement** :
   - Vérifier que l'abonnement est bien configuré
   - Ajouter les termes et conditions si nécessaire

### 6.2 Archiver et soumettre

1. **Dans Xcode** :
   - Sélectionner "Any iOS Device" comme destination
   - Product → Archive
   - Attendre la fin de l'archivage

2. **Dans la fenêtre Organizer** :
   - Sélectionner l'archive
   - Cliquer sur "Distribute App"
   - Choisir "App Store Connect"
   - Suivre l'assistant

3. **Une fois uploadé** :
   - Aller sur App Store Connect
   - Sélectionner le build
   - Remplir les informations de révision
   - Soumettre pour révision

### 6.3 Informations de révision Apple

Apple va tester votre app, y compris l'abonnement. Préparez :

1. **Compte de démonstration** (si nécessaire) :
   - Créer un compte test avec abonnement actif
   - Fournir les identifiants à Apple

2. **Notes pour l'équipe de révision** :
   ```
   Cette application utilise Sign in with Apple pour l'authentification.
   
   L'application offre 5 requêtes gratuites, puis propose un abonnement mensuel 
   à 15€ pour des requêtes illimitées.
   
   Pour tester :
   1. Se connecter avec Sign in with Apple
   2. Faire 5 requêtes (utiliser le compteur visible en bas)
   3. À la 6ème requête, l'écran d'abonnement s'affiche
   4. L'abonnement peut être testé avec un compte Sandbox
   ```

---

## 7. Dépannage

### Problème : "Product ID not found"

**Solution** :
- Vérifier que le Product ID dans `SubscriptionManager.swift` correspond exactement à celui dans App Store Connect
- Attendre 2-3 heures après création du produit (propagation Apple)
- Vérifier que le produit est bien "Ready to Submit"

### Problème : "Sign in with Apple failed"

**Solution** :
- Vérifier que la capability est bien activée dans Xcode
- Vérifier que Sign in with Apple est activé pour votre App ID dans le Developer Portal
- Sur simulateur : Aller dans Réglages → Apple ID et se connecter

### Problème : Le compteur ne se réinitialise pas

**Solution** :
- En mode Debug, utilisez le bouton dans Paramètres pour réinitialiser
- En production, le compteur est persistant (UserDefaults)
- Pour reset complet : désinstaller et réinstaller l'app

### Problème : L'abonnement ne se restaure pas

**Solution** :
- Utiliser le bouton "Restaurer les achats" dans les paramètres
- Vérifier que vous êtes connecté avec le même Apple ID
- En test Sandbox, vérifier que le compte Sandbox est actif

---

## 8. Vérification de la configuration

### Checklist avant publication :

- [ ] Bundle ID configuré et correspond à App Store Connect
- [ ] Capabilities ajoutées (Sign in with Apple + In-App Purchase)
- [ ] Product ID dans le code = Product ID dans App Store Connect
- [ ] Produit d'abonnement créé et "Ready to Submit"
- [ ] Prix configuré (15€/mois pour la France)
- [ ] Sandbox Tester créé
- [ ] Tests effectués sur simulateur avec StoreKit Configuration
- [ ] Tests effectués sur device avec Sandbox Account
- [ ] Tous les fichiers ajoutés au projet Xcode
- [ ] L'app compile sans erreur
- [ ] Screenshots préparés pour App Store
- [ ] Privacy Policy (si nécessaire)
- [ ] Notes de révision préparées

---

## 9. Fichiers modifiés/créés

### Fichiers créés :
- ✅ `Models/AuthenticationManager.swift` - Gestion Sign in with Apple
- ✅ `Models/SubscriptionManager.swift` - Gestion StoreKit 2 et abonnements
- ✅ `Models/UsageManager.swift` - Compteur de requêtes
- ✅ `Views/LoginView.swift` - Écran de connexion
- ✅ `Views/SubscriptionView.swift` - Écran d'abonnement
- ✅ `Views/SettingsView.swift` - Paramètres et gestion du compte

### Fichiers modifiés :
- ✅ `App/BrightnessChatApp.swift` - Ajout des managers et logique d'authentification
- ✅ `ViewModels/ChatViewModel.swift` - Vérification quota et incrémentation compteur
- ✅ `Views/ChatView.swift` - Intégration abonnement et paramètres
- ✅ `Views/ComposerView.swift` - Affichage du quota restant

---

## 10. Support

En cas de problème :

1. **Documentation officielle Apple** :
   - [StoreKit 2](https://developer.apple.com/documentation/storekit)
   - [Sign in with Apple](https://developer.apple.com/sign-in-with-apple/)
   - [In-App Purchase](https://developer.apple.com/in-app-purchase/)

2. **Tester l'implémentation** :
   ```bash
   # Vérifier que tous les fichiers sont présents
   ls -la front/ios/BrightnessChat/BrightnessChat/Models/
   ls -la front/ios/BrightnessChat/BrightnessChat/Views/
   ```

3. **Consulter les logs Xcode** :
   - Vérifier la console pour les erreurs StoreKit
   - Activer les logs détaillés si nécessaire

---

**Prêt à lancer !** 🚀

Votre application est maintenant configurée pour :
- ✅ Authentification avec Sign in with Apple
- ✅ 5 requêtes gratuites
- ✅ Abonnement mensuel à 15€
- ✅ Requêtes illimitées pour les abonnés
- ✅ Gestion complète du compte dans les paramètres

