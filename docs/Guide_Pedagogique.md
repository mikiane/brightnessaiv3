# Guide pédagogique (débutant)

Ce document explique, pas à pas, comment fonctionne BrightnessAI v3.

## 1. Vue d’ensemble
- `lib__config.py`: charge la configuration (.env) et fournit un logger unique.
- `lib__llm_models.py`: point d’entrée unifié pour appeler différents LLM.
- `streaming_api.py`: API Flask de chat (stream/standard).
- `transformers_api.py`: API Flask texte→résumé/transformations/podcast/transcription.
- `alter_brain_api.py`: API d’indexation/recherche de contexte et exécution de scripts en streaming.
- `lib__auto_watch_template.py` + `lib__common_tasks.py`: coeur des veilles `auto_watch_*_v2.py`.

## 2. Comment une veille fonctionne
1) Un script `auto_watch_*_v2.py` appelle une factory (ex: `create_ted_watch`) qui crée un `AutoWatchBot`.
2) Le bot construit un prompt standard (via `build_watch_command`) et collecte les sources (URLs/RSS).
3) Pour chaque source, `lib__common_tasks` récupère le contenu, fabrique un prompt contextuel et appelle le LLM.
4) Les résultats agrégés sont nettoyés puis envoyés par e-mail (via `lib__agent_buildchronical.mail_html`).

## 3. APIs
- `POST /stream_chat` (streaming_api): JSON {consigne, texte, model?} → flux texte.
- `POST /chat` (streaming_api): JSON {consigne, texte, model?, temperature?} → texte.
- `POST /sumup` (transformers_api): fichier + email → résumés par fichier envoyé par e-mail.
- `POST /transform` (transformers_api): texte + instruction + email → texte transformé envoyé.
- `POST /podcast` (transformers_api): texte + email → MP3 envoyé.
- `POST /whisper` (transformers_api): audio + email → transcription .txt envoyée.
- `POST /buildindex` (alter_brain_api): upload (zip/dossier) → brain_id.
- `POST /searchcontext` (alter_brain_api): texte + brain_id → contexte.
- `POST /streamtasks` (alter_brain_api): script JSON → sortie en flux.

## 4. Configuration
- Copier `.env` à la racine (voir variables dans `lib__config.py`).
- Clés critiques: `OPENAI_API_KEY` et `DEFAULT_MODEL`.
- Chemins: `PODCASTS_PATH`, `LOCALPATH`.

## 5. Journalisation & erreurs
- Utiliser `config.logger` pour tous les logs.
- Remplacer `print` par `logger.info/debug/error`.
- Remplacer `sys.exit()` par des exceptions explicites.

## 6. Déploiement Cron
- Utiliser les scripts `auto_watch_*_v2.py` (cf. exemples en tête de `cron.txt`).

## 7. Dépannage
- Vérifier `app.log` et la sortie standard.
- Tester localement: `python streaming_api.py` puis appeler l’API avec curl/Postman.

## 8. Ressources
- Guide de migration: `MIGRATION_GUIDE.md`
- Guide cron: `MIGRATION_CRON.md` 