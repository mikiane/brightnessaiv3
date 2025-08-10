from pydub import AudioSegment
import lib_genpodcasts
import random
from datetime import date, datetime
import locale
import json
import os
import requests
import time
from urllib.parse import unquote
from queue import Queue
from openai import OpenAI
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build

# Import centralized configuration
from libs import lib__agent_buildchronical
from libs import lib__transformers
from libs import lib__embedded_context
from libs import lib__config as config
logger = config.logger

# Configuration
DESTINATAIRES_TECH = config.DESTINATAIRES_TECH
PODCASTS_PATH = config.PODCASTS_PATH
DEFAULT_MODEL = config.DEFAULT_MODEL
ACAST_API_KEY = config.ACAST_API_KEY
LOCALPATH = config.LOCALPATH

## PODCAST VEILLE #1 ##
# Génération d'une liste de livres pour veille podcast
url_list = [
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

# Getting the current date
current_date = datetime.now()

# Formatting the date as "dd month yyyy"
formatted_date = current_date.strftime("%d %B %Y")
        
command = (
    "Nous sommes le "
    + formatted_date
    + "\nA partir du texte suivant entre ___ , contenant les derniers articles sur la géopolitique, "
    "        extraire TOUS les articles datant d'il y a moins de 48 heures. "
    "        Commencer par le titre traduit en français et la date de l'article.  "
    "        N'hésite pas à développer si besoin afin d'expliquer les termes techniques ou jargonneux à une audience grand public "
    "        Aucun article datant de moins de 48 heures ne doit etre oublié. Ne converse pas. Ne conclue pas. "
    "        Ne pas générer d'introduction ni de conclusion, juste l'article'. "
    "        Si il n'y a pas d'article, ne pas dire qu'il n'y pas d'article, renvoyer une chaine vide." 
    "        Ne pas commencer par Voici l'artcie... Mais directement démarrer par l'article'. Respecter ces consignes strictement. "
)

# generation de la veille
model = DEFAULT_MODEL

responses = [lib_genpodcasts.process_url(command, url, model, "", "") for url in url_list]
res = "<br><br>".join(responses)

text_veille = str(res.replace("```html", "")).replace("```", "")

logger.info(text_veille)

# Génération du script via LLM
prompt = """
Contexte : Vous êtes chargé(e) d’écrire un script en français complet pour un podcast quotidien de revue de presse sur la géopolitique intitulé Le monde Aujourd’hui. Ce podcast doit être informatif, factuel et engageant, conçu pour un auditoire curieux mais non-expert. L’objectif est de fournir un contenu captivant et accessible tout en restant rigoureux.
"""

text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model, 14000)
logger.info(text_final)

# TTS et montage
voice_id = "Fgn8wInzqZU1U5EP2qp0"
randint = random.randint(0, 100000)
final_filename = PODCASTS_PATH + "final_podcast" + str(randint) + str(date.today()) + ".mp3"
combined = AudioSegment.from_mp3(str(LOCALPATH) + "sounds/intro.mp3")
lib__agent_buildchronical.texttospeech(text_final, voice_id, final_filename)
AudioSegment.from_mp3(final_filename)
combined += AudioSegment.from_mp3(final_filename)
combined += AudioSegment.from_mp3(str(LOCALPATH) + "sounds/outro.mp3")
combined.export(final_filename, format='mp3')

titre = "Le monde aujourd'hui épisode du " + str(date.today())
text = text_final
audio = final_filename
email = "michel@brightness.fr"
subtitle = "Le monde aujourd'hui : le podcast géopolitique par l'IA qui vous permet de rester à la page !"
lib__agent_buildchronical.mailaudio(titre, audio, text, email)

# POST D'UN EPISODE SUR ACAST
logger.debug(f"Clé API utilisée : {ACAST_API_KEY}")
headers = {"x-api-key": ACAST_API_KEY}
url = "https://open.acast.com/rest/shows/677268f0310557bf4f6d31a6/episodes"
logger.info("Début de post de podcast")

payload = {
    'title': titre,
    'subtitle': subtitle,
    'status': 'published',
    'summary': text,
}

file_path = audio
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} n'existe pas ou le chemin est incorrect.")
if os.path.getsize(file_path) == 0:
    raise ValueError(f"Le fichier {file_path} est vide.")

files = [('audio', (os.path.basename(file_path), open(file_path, 'rb'), 'audio/mpeg'))]
logger.info("début d'envoi de podcast")
response = requests.post(url, headers=headers, data=payload, files=files)
logger.info("fin d'envoi de podcast")
logger.info(f"Statut : {response.status_code}")
logger.debug(f"En-têtes de la réponse : {response.headers}")
logger.debug(f"Réponse : {response.text}")



