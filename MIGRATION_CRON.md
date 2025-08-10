# Guide de Migration des Tâches Cron

## 📋 Correspondance des scripts

| Ancien script | Nouveau script | Fréquence suggérée |
|--------------|----------------|-------------------|
| `auto_watch_ted.py` | `auto_watch_ted_v2.py` | Hebdomadaire |
| `auto_watch_publicspeaking.py` | `auto_watch_publicspeaking_v2.py` | Hebdomadaire |
| `auto_watch_ld.py` | `auto_watch_ld_v2.py` | Hebdomadaire |
| `auto_watch_debatsetidees.py` | `auto_watch_debatsetidees_v2.py` | Quotidien |
| `auto_watch_allinno.py` | `auto_watch_allinno_v2.py` | Quotidien |
| `auto_watch_trensdpotting.py` | `auto_watch_trensdpotting_v2.py` | Hebdomadaire |

## 🔧 Exemple de migration cron

### Ancien crontab
```bash
# TED Watch - Lundi 8h
0 8 * * 1 cd /path/to/project && python auto_watch_ted.py

# Tech Watch - Tous les jours 7h
0 7 * * * cd /path/to/project && python auto_watch_allinno.py
```

### Nouveau crontab
```bash
# TED Watch - Lundi 8h
0 8 * * 1 cd /path/to/project && python auto_watch_ted_v2.py

# Tech Watch - Tous les jours 7h
0 7 * * * cd /path/to/project && python auto_watch_allinno_v2.py
```

## 📝 Étapes de migration recommandées

### 1. Test en parallèle (1 semaine)
```bash
# Garder les anciens scripts ET ajouter les nouveaux
0 8 * * 1 cd /path/to/project && python auto_watch_ted.py
5 8 * * 1 cd /path/to/project && python auto_watch_ted_v2.py >> logs/ted_v2.log 2>&1
```

### 2. Basculement progressif
- Semaine 1 : Migrer `auto_watch_ted_v2.py`
- Semaine 2 : Migrer `auto_watch_publicspeaking_v2.py` et `auto_watch_ld_v2.py`
- Semaine 3 : Migrer les scripts quotidiens

### 3. Validation
```bash
# Vérifier les logs
tail -f logs/ted_v2.log

# Comparer les emails générés
```

### 4. Nettoyage
```bash
# Après validation complète (2-3 semaines)
rm auto_watch_ted.py
rm auto_watch_publicspeaking.py
rm auto_watch_ld.py
rm auto_watch_debatsetidees.py
rm auto_watch_allinno.py
rm auto_watch_trensdpotting.py
```

## 🎯 Avantages du nouveau système

1. **Maintenance simplifiée** : Un seul template à maintenir
2. **Ajout facile** : Créer un nouveau bot en 5 lignes
3. **Configuration centralisée** : Tout dans `lib__config.py`
4. **Logging amélioré** : Suivi détaillé des exécutions
5. **Code réduit de 81%** : Moins de bugs potentiels

## 🆕 Créer un nouveau bot de veille

```python
# nouveau_bot.py
from lib__auto_watch_template import AutoWatchBot
import lib__config as config

if __name__ == "__main__":
    bot = AutoWatchBot("Mon Bot", "mon sujet", "email@example.com")
    bot.add_urls(["https://example.com"])
    bot.add_rss_feeds(["https://example.com/rss"])
    bot.run(hours_ago=24, model=config.DEFAULT_MODEL)
```

## 📊 Monitoring

### Script de monitoring simple
```bash
#!/bin/bash
# check_watches.sh

echo "=== État des veilles ==="
for script in auto_watch_*_v2.py; do
    echo -n "$script: "
    if ps aux | grep -v grep | grep -q "$script"; then
        echo "✅ En cours"
    else
        echo "⏸️  Arrêté"
    fi
done

echo ""
echo "=== Dernières exécutions ==="
ls -lt logs/*.log | head -10
```

## ⚠️ Points d'attention

1. **Dépendances** : S'assurer que `feedparser` est installé
2. **Permissions** : Les nouveaux scripts doivent être exécutables
3. **Logs** : Créer le dossier `logs/` si nécessaire
4. **Emails** : Vérifier que les adresses email sont correctes
5. **Modèle LLM** : Vérifier `DEFAULT_MODEL` dans `.env`

---

*Guide créé pour la migration Phase 3 - Scripts auto_watch* 