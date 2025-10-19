# 📱 Installation sur iPhone

Guide complet pour installer **BrightnessChat** sur votre iPhone.

---

## 📋 Prérequis

### ✅ Matériel
- Mac avec Xcode installé
- iPhone (iOS 16.0 ou supérieur)
- Câble USB Lightning ou USB-C

### ✅ Compte Apple
- Apple ID (gratuit)
- Pas besoin de compte développeur payant pour les tests personnels

---

## 🚀 Installation en 5 Étapes

### Étape 1 : Connecter l'iPhone

1. **Brancher l'iPhone** au Mac avec le câble USB

2. **Sur l'iPhone**, si c'est la première fois :
   - Message "Faire confiance à cet ordinateur ?"
   - Déverrouiller l'iPhone
   - Appuyer sur **"Faire confiance"**
   - Entrer le code de l'iPhone

3. **Attendre** que l'iPhone apparaisse dans Xcode (icône en haut à gauche)

---

### Étape 2 : Ouvrir le Projet dans Xcode

```bash
cd "/Users/michel/Dropbox (Compte personnel)/1-DEVELOPPEMENTS/Git/brightnessaiv3/front/ios"
open BrightnessChat/BrightnessChat.xcodeproj
```

Ou double-cliquer sur `BrightnessChat.xcodeproj`

---

### Étape 3 : Configurer le Signing (Signature)

**1. Sélectionner le projet**
- Cliquer sur **BrightnessChat** (bleu) en haut du navigateur

**2. Onglet "Signing & Capabilities"**
- Target : **BrightnessChat**
- Cocher **"Automatically manage signing"**

**3. Team**
- Cliquer sur le menu **Team**
- Si vide, cliquer sur **"Add an Account..."**
  - Se connecter avec votre **Apple ID**
  - Fermer la fenêtre
- Sélectionner votre **nom/email** dans Team

**4. Bundle Identifier (si erreur)**
- Si "Failed to register bundle identifier" :
- Changer `fr.brightness.BrightnessChat` en :
  ```
  fr.brightness.BrightnessChat.michel
  ```
  (ou votre prénom)

---

### Étape 4 : Sélectionner votre iPhone

**En haut à gauche de Xcode** :

1. Cliquer sur le menu qui affiche le simulateur
2. Sélectionner **votre iPhone** dans la liste
   ```
   📱 iPhone de Michel
   ```

---

### Étape 5 : Compiler et Installer

**1. Build (⌘B)**
- Attendre la fin de la compilation
- Si erreur, voir section "Dépannage" ci-dessous

**2. Run (⌘R) ou cliquer sur ▶️**
- Xcode va installer l'app sur votre iPhone
- **Première fois** : peut prendre 1-2 minutes

**3. Sur l'iPhone** (première installation uniquement) :
   
   **Message d'erreur** : "Développeur d'entreprise non approuvé"
   
   **Solution** :
   1. Aller dans **Réglages** (Settings) de l'iPhone
   2. **Général**
   3. **Gestion des appareils** (ou VPN & Gestion de l'appareil)
   4. Sous "APP DÉVELOPPEUR", appuyer sur **votre Apple ID**
   5. Appuyer sur **"Faire confiance à..."**
   6. Confirmer **"Se fier"**
   7. Revenir à l'écran d'accueil
   8. L'app **BrightnessChat** peut maintenant se lancer ✅

**4. L'app se lance automatiquement** sur votre iPhone ! 🎉

---

## 🎯 Raccourcis Rapides

Une fois la configuration initiale faite :

```
1. Brancher l'iPhone
2. Dans Xcode : sélectionner l'iPhone (menu en haut)
3. Appuyer sur ▶️ ou ⌘R
```

L'app s'installe et se lance automatiquement !

---

## 🐛 Dépannage

### ❌ "iPhone is locked"

**Solution** : Déverrouiller l'iPhone

---

### ❌ "Failed to launch... devicectl error"

**Cause** : Connexion USB instable

**Solution** :
1. Débrancher et rebrancher l'iPhone
2. Redémarrer Xcode
3. Réessayer

---

### ❌ "The device is not unlocked. Please unlock the device..."

**Solution** :
1. Déverrouiller l'iPhone
2. Garder l'écran allumé pendant l'installation
3. Relancer (⌘R)

---

### ❌ "Untrusted Developer"

**Solution** : Voir Étape 5, point 3 ci-dessus (Réglages > Général > Gestion des appareils)

---

### ❌ "Code signing is required for product type 'Application'"

**Solution** :
1. Projet > BrightnessChat
2. Signing & Capabilities
3. Team : Sélectionner votre Apple ID
4. Si besoin, changer le Bundle Identifier

---

### ❌ "Failed to register bundle identifier"

**Cause** : `fr.brightness.BrightnessChat` déjà pris

**Solution** : Changer le Bundle Identifier
```
fr.brightness.BrightnessChat.michel
```
(ou votre prénom/pseudo unique)

Où changer :
1. Projet > BrightnessChat
2. Target > BrightnessChat
3. General > Identity > **Bundle Identifier**

---

### ❌ "Unable to install... This app cannot be installed..."

**Cause** : Limite des 3 apps en développement gratuit atteinte

**Solution** :
1. Sur l'iPhone : supprimer une app en développement
2. Ou attendre 7 jours
3. Ou souscrire au programme Apple Developer (99€/an)

---

## 📊 Durées Normales

| Action | Durée |
|--------|-------|
| Première connexion iPhone | 30s - 1min |
| Configuration Signing | 2-3 min |
| Première compilation | 1-2 min |
| Première installation | 1-2 min |
| Installations suivantes | 10-30s |

---

## 🔄 Mises à Jour de l'App

Pour mettre à jour l'app après modification du code :

```
1. Modifier le code dans Xcode
2. iPhone branché (ou pas besoin si debug sans fil configuré)
3. Appuyer sur ▶️ ou ⌘R
```

L'app est automatiquement mise à jour et relancée !

---

## 📱 Debug Sans Fil (Optionnel)

Pour installer sans câble :

**1. Première configuration** (avec câble) :
1. iPhone branché
2. Window > Devices and Simulators
3. Sélectionner votre iPhone
4. Cocher **"Connect via network"**

**2. Ensuite** :
- Débrancher le câble
- L'iPhone apparaît avec une icône réseau
- Installer normalement avec ⌘R

**Prérequis** :
- iPhone et Mac sur le **même réseau Wi-Fi**
- iPhone déverrouillé lors de la première connexion sans fil

---

## 🎨 Changer la Configuration

Pour tester avec différentes configurations (brightness, oraldubac, etc.) :

**1. Éditer `AppConfig.swift`** :
```swift
static let defaultConfigFile = "brightness"  // Changer ici
```

**2. Recompiler et installer** :
```
⌘R
```

**3. L'app sur l'iPhone** utilise maintenant la nouvelle configuration !

---

## 📦 Distribution (Optionnel)

### TestFlight (Bêta Testing)

Pour partager l'app à d'autres personnes :

1. **Créer une archive** :
   - Product > Archive
   
2. **Uploader vers App Store Connect** :
   - Window > Organizer
   - Sélectionner l'archive
   - Distribute App > App Store Connect
   
3. **TestFlight** :
   - Inviter des testeurs par email
   - Ils peuvent installer via l'app TestFlight

**Prérequis** : Compte Apple Developer (99€/an)

---

### App Store (Production)

Pour publier sur l'App Store :

1. Archive créée (voir ci-dessus)
2. App Store Connect : Créer l'app
3. Soumettre pour révision Apple
4. Attendre validation (1-7 jours)
5. Publication

**Prérequis** :
- Compte Apple Developer (99€/an)
- Conformité aux guidelines Apple
- Icônes, screenshots, description, etc.

---

## 💡 Astuces

### Console et Logs

Pour voir les logs de l'iPhone :

1. **Window > Devices and Simulators**
2. Sélectionner votre iPhone
3. Cliquer sur **"Open Console"**
4. Lancer l'app
5. Voir les `print()` en temps réel (🔍, ✅, ❌)

### Performances

Sur iPhone physique :
- ✅ Plus rapide que le simulateur
- ✅ Performance réelle
- ✅ Test du réseau réel

---

## ✅ Checklist Complète

- [ ] iPhone branché et reconnu
- [ ] Xcode ouvert avec le projet
- [ ] Signing configuré avec Apple ID
- [ ] Bundle Identifier unique (si besoin)
- [ ] iPhone sélectionné (menu en haut)
- [ ] Compilation réussie (⌘B)
- [ ] Installation lancée (⌘R)
- [ ] Développeur approuvé sur iPhone (Réglages)
- [ ] App lancée avec succès
- [ ] Tests fonctionnels OK

---

## 🎉 Félicitations !

Votre app **BrightnessChat** est maintenant installée sur votre iPhone !

Vous pouvez :
- ✅ L'utiliser en mobilité
- ✅ Tester avec une vraie connexion réseau
- ✅ La montrer à d'autres personnes
- ✅ La garder sur votre téléphone (valide 7 jours sans recertification)

---

## 📞 Support

**Besoin d'aide ?**

Vérifier :
1. Les logs dans la console Xcode (⌘⇧Y)
2. Les erreurs de signing
3. La connexion USB
4. La version iOS de votre iPhone (≥ 16.0)

---

**Version** : 1.0  
**Date** : Octobre 2024  
**Compatible** : iOS 16.0+

