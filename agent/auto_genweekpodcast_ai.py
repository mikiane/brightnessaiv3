
from pydub import AudioSegment
import os
from libs import lib__agent_buildchronical
import random
from datetime import date, datetime
import locale
from libs import lib__transformers
import json
from libs import lib__embedded_context
import requests
import time
from urllib.parse import unquote
from queue import Queue
from openai import OpenAI
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import lib_genpodcasts

# Import centralized configuration
from libs import lib__config as config
logger = config.logger

# Config vars
DESTINATAIRES_TECH = config.DESTINATAIRES_TECH
PODCASTS_PATH = config.PODCASTS_PATH
DEFAULT_MODEL = config.DEFAULT_MODEL
ACAST_API_KEY = config.ACAST_API_KEY
LOCALPATH = config.LOCALPATH
model = DEFAULT_MODEL


def fetch_podcast_summaries(api_key, podcast_id, limit):
    """
    Récupère les résumés des épisodes d'un podcast et les concatène.

    Args:
        api_key (str): La clé API pour authentification.
        podcast_id (str): L'identifiant du podcast.
        limit (int): Nombre d'épisodes à récupérer.

    Returns:
        str: Les résumés des épisodes concaténés avec deux sauts de ligne entre chaque.
    """
    episodes_url = f'https://open.acast.com/rest/shows/{podcast_id}/episodes'
    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }

    try:
        response = requests.get(episodes_url, headers=headers)
        response.raise_for_status()
        episodes_data = response.json()
        episodes = episodes_data[:limit] if limit else episodes_data
        summaries = []
        for episode in episodes:
            summary = episode.get('summary', 'Pas de résumé disponible')
            summaries.append(summary)
        result = '\n\n'.join(summaries)
        return result
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'Erreur HTTP: {http_err}')
        return None
    except Exception as err:
        logger.error(f'Erreur: {err}')
        return None


api_key = ACAST_API_KEY
podcast_id = "67328a919e7b27e0ac078578"
limit = 6

result = fetch_podcast_summaries(api_key, podcast_id, limit)
if result:
    logger.info(result)

text_veille = result

prompt = """

Contexte : Vous êtes chargé(e) d’écrire un script complet pour la version hebdomadaire du podcast L'IA Aujourd'hui. C'est une revue de presse sur l’intelligence artificielle intitulé *L’IA cette semaine*, présenté par Michel Lévy Provençal. Ce podcast doit être informatif, factuel et engageant, conçu pour un auditoire curieux mais non-expert. L’objectif est de fournir un contenu captivant et accessible tout en restant rigoureux.

Consignes spécifiques :
Le texte fourni correspond au script des 6 derniers jours d'actu de l'IA. Vous devez rédiger un script de podcast complet, comprenant une introduction, toutes les actualités de la semaine (reprendre le contenu de chacun des jours), et une conclusion. Voici les consignes détaillées :
- Structure du script :
  - Introduction :
    - Courte et percutante, introduire le podcast avec la phrase standard :  
      *"Bonjour à toutes et à tous, bienvenue dans *L’IA cette semaine*, le podcast de l’IA par l’IA qui vous permet de rester à la page !"*  
    - Suivre par une phrase résumant les sujets de la semaine, concise et dynamique :  
      *"Cette semaine : [grandes thématiques du jour]. C’est parti !"*
  - Les grandes actualités de la semaine :  
    Reprendre le script de chaque jour.
    Ne résume pas, ne tronque pas, ne simplifie pas. Reprendre chaque news dans son intégralité.
  - Transitions :  
    Utilisez des transitions naturelles entre les sujets, en assurant une narration fluide. Variez les styles pour éviter la répétition, mais restez sobre : pas d’abus de questions rhétoriques ou d’effets de style inutiles.
  - Conclusion :  
    Ne pas faire de récapitulatif court. Tout de suite après la dernière actualité, conclure avec la phrase standard :  
      *"Voilà qui conclut notre épisode de cette semaine. Merci de nous avoir rejoints, et n’oubliez pas de vous abonner pour ne manquer aucune de nos discussions passionnantes. À très bientôt dans *L’IA Aujourd’hui* !"*

- Ton et style :
  - Utiliser un français litteraire, n'buse pas des adjectifs, soit simple et direct
- Accessible mais rigoureux : Évitez un ton trop technique ou professoral. Expliquez les concepts sans les simplifier à outrance.
  - Engageant et fluide : Adoptez un style journalistique équilibré, dynamique mais sans excès d’emphase.
  - Informé et crédible : Appuyez-vous sur des faits solides, sourcés et vérifiés, en évitant les conjectures.
  - Sans redondance : Limitez les répétitions ou les apartés trop longs.
  - Unifier les thématiques : Lorsque possible, établissez des liens entre les sujets pour créer une narration cohérente et captivante.
  - N"utilise pas de titre pour chaque news.
  - N'insiste pas sur les questions rhétoriques pour chaque news et n'abuse pas des commentaires génériques relatifs à des questions, ethiques, philosophiques ou politiques liées à ces news. 
  - Contente toi de donner les faits.
Exemple de début de script attendu :
*"Bonjour à toutes et à tous, bienvenue dans *L’IA Aujourd’hui*, le podcast de l’IA par l’IA qui vous permet de rester à la page ! Aujourd’hui : des décisions politiques influencées par des modèles d’IA, l’audacieuse expansion de GitHub vers des outils multi-modèles, et une analyse des tensions croissantes au sein des grandes entreprises technologiques. C’est parti !"*

Objectif final : Produire un script détaillé, prêt à être lu, d’une durée de **10 à 15 minutes**, soit environ **30 000 signes**, en intégrant les actualités fournies de manière exhaustive et captivante.

Instructions pour les actualités fournies :
1. Développez chaque sujet avec rigueur en exploitant les détails, les chiffres et les exemples fournis dans les sources.
2. Ignorez les actualités génériques ou manquant d’informations pertinentes.
"""

text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model, 14000)

logger.info(text_final)

#envoi de la newsletter
#title = "AI PODCAST : veille sur l'IA"
#email = "contact@brightness.fr"
#lib__agent_buildchronical.mail_html(title, text_final, email)

# Task : task7

# Appeler l'API elevenLabs et construire un podcast

# text_final = "Bienvenue dans //L'IA aujourd'hui : le podcast de l'IA par l'IA qui vous permet de rester à la page !// Aujourd'hui, nous allons explorer deux sujets fascinants et d'actualité : l'incertitude des travailleurs étrangers dans le secteur technologique américain face aux politiques d'immigration, et la question de savoir si l'intelligence artificielle peut remplacer les traducteurs humains."
# creation de l'audio
voice_id = "Fgn8wInzqZU1U5EP2qp0" # MLP   eKZsbKN3buNViPVgJwQr
# voice_id = "TxGEqnHWrfWFTfGW9XjX" # Josh
# randint = randint(0, 100000)
# filename = PODCASTS_PATH + "podcast" + str(randint) + ".mp3"
# texttospeech(text, voice_id, filename)

randint = random.randint(0, 100000)
final_filename = PODCASTS_PATH + "final_podcast" + str(randint) + str(date.today()) + ".mp3"
combined = AudioSegment.from_mp3(str(LOCALPATH) + "sounds/intro.mp3")
# gestion des intonations.
lib__agent_buildchronical.texttospeech(text_final, voice_id, final_filename)
audio_segment = AudioSegment.from_mp3(final_filename)
combined += audio_segment
combined += AudioSegment.from_mp3(str(LOCALPATH) + "sounds/outro.mp3")

# Save the final concatenated audio file
combined.export(final_filename, format='mp3')

# titre = "Dailywatch \n du \n" + str(date.today())
# input_audiofile = filename
# output_videofile = "datas/podcast" + str(randint) + ".mp4"

## creation de la video avec les fichiers d'entrée appropriés
# create_video_with_audio(input_audiofile, titre, output_videofile)


titre = "L'IA cette semaine épisode du " + str(date.today())
text = text_final
audio = final_filename
email = "michel@brightness.fr"  # Remplacez 'destinataire' par 'email'
subtitle = "L'IA cette semaine : le podcast de l'IA par l'IA qui vous permet de rester à la page !"
# Appel de la fonction mailaudio
lib__agent_buildchronical.mailaudio(titre, audio, text, email)

# Conversion d'un fichier audio au format Acast
input_file = audio
output_file = input_file
# Déjà au bon format, log d'info seulement
logger.info(f"Fichier converti avec succès : {output_file}")



