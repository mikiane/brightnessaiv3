#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script: auto_genpodcast_geo_2.py
Description: Génère un podcast quotidien Géopolitique en calquant l'architecture de auto_genpodcast_ai.py
- Veille multi-sites géopolitiques → synthèse détaillée (prompt enrichi)
- TTS + montage intro/outro
- Envoi email + publication Acast (flux Géopolitique)
"""

# Standard library
import os
import random
from datetime import datetime, date

# Third-party
from pydub import AudioSegment
import requests

# Local
from libs import lib__agent_buildchronical
from libs import lib__config as config
import lib_genpodcasts

logger = config.logger

# Configuration centrale
DEFAULT_MODEL = config.DEFAULT_MODEL
PODCASTS_PATH = config.PODCASTS_PATH
ACAST_API_KEY = config.ACAST_API_KEY
LOCALPATH = config.LOCALPATH


def get_urls_geopolitics() -> list:
    """Retourne la liste des sources géopolitiques (statique)."""
    return [
        "https://atlas-report.com/",
        "https://www.foreignaffairs.com/",
        "https://thediplomat.com/",
        "https://foreignpolicy.com/",
        "https://worldview.stratfor.com/",
        "https://nationalinterest.org/",
        "https://www.chathamhouse.org/",
        "https://hir.harvard.edu/",
        "https://www.worldpoliticsreview.com/",
        "https://www.the-american-interest.com/",
        "https://www.e-ir.info/",
        "https://www.globalpolicyjournal.com/",
    ]


def main() -> None:
    # Date courante
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d %B %Y")

    # Sources géopolitiques
    url_list = get_urls_geopolitics()

    # Commande d'extraction (veille) – consignes orientées géopolitique
    command = (
        "Nous sommes le "
        + formatted_date
        + "\nA partir du texte suivant entre ___ , contenant les derniers articles de géopolitique, "
        "extraire TOUS les articles datant d'il y a moins de 48 heures. "
        "Commencer par le titre traduit en français et la date de l'article. "
        "Développer si besoin afin d'expliquer les termes techniques à une audience non-experte. "
        "Ne pas générer d'introduction ni de conclusion, juste la liste d'articles. "
        "Si aucune actualité récente n'est détectée, renvoyer une chaîne vide. "
    )

    # Veille: modèle par défaut (évite les incompatibilités de certains modèles reasoning)
    model_veille = DEFAULT_MODEL
    try:
        mv = str(model_veille).lower()
        if mv.startswith("o1") or "reason" in mv or mv == "gpt-5":
            model_veille = "gpt-4o"
    except Exception:
        model_veille = DEFAULT_MODEL

    logger.info(f"Démarrage veille géopolitique ({len(url_list)} sources)")
    responses = [lib_genpodcasts.process_url(command, url, model_veille, "", "") for url in url_list]
    res = "<br><br>".join(responses)
    text_veille = str(res.replace("```html", "")).replace("```", "")

    logger.info("CONTENU VEILLE (GEO) — début")
    logger.info(text_veille)
    logger.info("CONTENU VEILLE (GEO) — fin")

    # Prompt de synthèse (complet), spécifique géopolitique
    prompt = """
Contexte : Vous êtes chargé(e) d’écrire un script en français complet (≤ 4 500 signes) pour un podcast quotidien de revue de presse Géopolitique intitulé « Le monde aujourd’hui ». 
Le podcast doit être informatif, factuel et accessible à un auditoire curieux mais non-expert.

Consignes de structure :
- Introduction courte et percutante, avec la phrase standard :
  "Bonjour et bienvenue dans Le monde aujourd’hui, le podcast géopolitique par l’IA qui vous permet de rester à la page !"
- En une phrase, annoncer les grandes thématiques du jour.
- Corps du script :
  - Traiter TOUTES les actualités détectées dans la veille.
  - Pour chaque actualité : replacer brièvement le contexte (acteurs, enjeux), donner les faits clés (dates, chiffres, décisions), et les implications possibles (régionales/globales) en restant factuel.
  - Expliquer les termes techniques sans jargonner, avec pédagogie, sans digressions idéologiques.
- Transitions naturelles entre sujets, ton journalistique sobre.
- Conclusion standard :
  "Voilà qui conclut notre épisode d’aujourd’hui. Merci de nous avoir rejoints, et n’oubliez pas de vous abonner pour ne manquer aucune de nos discussions passionnantes. À très bientôt dans Le monde aujourd’hui !"

Contraintes rédactionnelles :
- Français journalistique, précis, sans superlatifs inutiles.
- Pas de titres par actualité, enchaîner de manière fluide.
- Ne pas inventer d’informations, s’en tenir aux faits détectés dans la veille.
- Ne pas faire d’appel à l’action autre que la conclusion standard.
"""

    # Modèle de synthèse — demandé: GPT‑5
    model_synthese = "gpt-4o"
    text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model_synthese, 16000)

    logger.info("SCRIPT GÉOPOLITIQUE — début")
    logger.info(text_final)
    logger.info("SCRIPT GÉOPOLITIQUE — fin")

    # TTS et montage audio intro/outro
    voice_id = "Fgn8wInzqZU1U5EP2qp0"  # MLP
    randint_num = random.randint(0, 100000)
    final_filename = (
        PODCASTS_PATH + "final_podcast_geo_" + str(randint_num) + str(date.today()) + ".mp3"
    )

    combined = AudioSegment.from_mp3(str(LOCALPATH) + "sounds/intro.mp3")
    lib__agent_buildchronical.texttospeech(text_final, voice_id, final_filename)
    audio_segment = AudioSegment.from_mp3(final_filename)
    combined += audio_segment
    combined += AudioSegment.from_mp3(str(LOCALPATH) + "sounds/outro.mp3")
    combined.export(final_filename, format='mp3')

    # Envoi email
    titre = "Le monde aujourd'hui épisode du " + str(date.today())
    email = "michel@brightness.fr"
    subtitle = "Le monde aujourd'hui : le podcast géopolitique par l'IA qui vous permet de rester à la page !"
    lib__agent_buildchronical.mailaudio(titre, final_filename, text_final, email)

    # Publication Acast (flux GEO)
    logger.debug(f"Clé API Acast (présente): {bool(ACAST_API_KEY)}")
    headers = {"x-api-key": ACAST_API_KEY}
    url = "https://open.acast.com/rest/shows/677268f0310557bf4f6d31a6/episodes"
    logger.info("Début de post de podcast (GEO)")

    payload = {
        'title': titre,
        'subtitle': subtitle,
        'status': 'published',
        'summary': text_final,
    }

    file_path = final_filename
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas ou le chemin est incorrect.")
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"Le fichier {file_path} est vide.")

    files = [('audio', (os.path.basename(file_path), open(file_path, 'rb'), 'audio/mpeg'))]
    logger.info("début d'envoi de podcast (GEO)")
    response = requests.post(url, headers=headers, data=payload, files=files)
    logger.info("fin d'envoi de podcast (GEO)")
    logger.info(f"Statut : {response.status_code}")
    logger.debug(f"En-têtes de la réponse : {response.headers}")
    logger.info(f"Réponse : {response.text}")


if __name__ == "__main__":
    main()


