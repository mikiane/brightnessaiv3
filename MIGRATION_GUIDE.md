# Guide de Migration et Refactoring BrightnessAI v3

## 📊 Résumé des améliorations identifiées

### Problèmes majeurs détectés :
1. **Configuration éparpillée** : Chaque fichier charge `.env` individuellement
2. **Duplication de code** : Fonctions LLM dupliquées dans plusieurs fichiers
3. **Scripts répétitifs** : Les auto_watch_* contiennent 90% de code identique
4. **Imports désorganisés** : Imports dupliqués et non triés
5. **Absence de logging** : Difficile de débugger en production

## 🚀 Plan de migration par priorité

### Phase 1 : Configuration centralisée (FAIT ✅)

### Phase 2 : Migration des fonctions LLM (FAIT ✅)

### Phase 3 : Unifier les scripts auto_watch_* (FAIT ✅)
- Template `lib__auto_watch_template.py` + `lib__common_tasks.py`
- Entrées `*_v2.py` minimalistes, prêtes pour cron

### Phase 4 : Nettoyage des imports (FAIT ✅)
- Bascule complète vers `lib__config`
- Ajouts variables manquantes
- Suppression des doublons
- Nettoyage legacy (FAIT ✅):
  - Supprimés: `auto_watch_trensdpotting.py`, `auto_watch_debatsetidees.py`, `auto_watch_ld.py`, `auto_watch_publicspeaking.py`, `auto_watch_ted.py`, `auto_watch_allinno.py`
  - À utiliser dans cron: `auto_watch_*_v2.py` (voir exemple dans `cron.txt`)

### Phase 5 : Logging structuré et gestion d’erreurs (EN COURS 🔄)
- Logger central adopté dans les modules clés et services
- Normalisation `print` -> `logger.*`, `sys.exit()` -> exceptions

## 📝 Checklist de migration

### Nettoyage (Phase 4) ✅
- [x] Retirer `load_dotenv()` restants
- [x] Trier les imports
- [x] Variables manquantes dans `lib__config.py`
- [x] Suppression legacy `auto_watch_*` au profit des `*_v2.py`

## 🔧 Notes d’exploitation
- Cron: préférez les `*_v2.py` (cf. en-tête de `cron.txt` pour exemples)
- Logs: fichier `app.log` + stdout via `config.logger`

## 🚦 Statut actuel
- Phases 1–4: ✅
- Phase 5: 🔄 en cours 