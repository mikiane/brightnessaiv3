#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Nom du script: generate_podcast_ai.py
Description: Ce script génère des podcasts automatiquement basés sur des flux RSS et des sources d'actualités sur l'IA.
Auteur: Michel Levy Provencal
"""

# Standard library imports
import os
import re
import csv
import random
from datetime import datetime, date
import tempfile
import json

# Third-party imports
from pydub import AudioSegment
import requests
from feedparser import parse
from urllib.parse import unquote

# Local imports
import lib_genpodcasts
from libs import lib__agent_buildchronical
from libs import lib__config as config
logger = config.logger

# Use configuration from lib__config
DEFAULT_MODEL = config.DEFAULT_MODEL
PODCASTS_PATH = config.PODCASTS_PATH
ACAST_API_KEY = config.ACAST_API_KEY
LOCALPATH = config.LOCALPATH

model = DEFAULT_MODEL


## PODCAST VEILLE #1 ##
# Génération d'une liste de livres pour veille podcast
"""url_list = ["https://www.artificialintelligence-news.com/"
            , "https://venturebeat.com/category/ai/"
            , "https://www.wired.com/tag/artificial-intelligence/"
            , "https://www.forbes.com/ai/"
            , "https://www.theguardian.com/technology/artificialintelligenceai"
            , "https://www.nature.com/natmachintell/"
            , "https://towardsdatascience.com/"
            , "https://openai.com/news/"
            , "https://neurips.cc/"
            , "https://www.theverge.com/ai-artificial-intelligence"
            , "https://techcrunch.com/tag/artificial-intelligence/"]
"""




"""url_list = ["https://www.artificialintelligence-news.com/"
            , "https://techcrunch.com/category/artificial-intelligence/"
            , "https://www.wsj.com/tech/ai"
            , "https://www.reuters.com/technology/artificial-intelligence/"
            , "https://venturebeat.com/category/ai/"
            , "https://www.lemondeinformatique.fr/intelligence-artificielle-154.html"
            , "https://insideainews.com/"
            , "https://openai.com/news/"
            , "https://neurips.cc/"
            , "https://www.theverge.com/ai-artificial-intelligence"]
"""





def get_urls_from_rss(rss_url: str) -> list:
    """
    Récupère les URLs contenues dans un flux RSS et les renvoie sous forme de liste.
    """
    # Parse du flux RSS
    feed = parse(rss_url)
    
    # Extraction des URLs dans une liste
    urls = []
    for entry in feed.entries:
        # La plupart du temps, l'URL se trouve dans l'attribut 'link'
        urls.append(entry.link)
    
    return urls

rss_feed = "https://flint.media/bots/feeds/eyJhbGciOiJIUzI1NiJ9.eyJib3RfaWQiOjEyNzYyLCJlZGl0aW9uIjoibGFzdCJ9.IswPZy0ZFMgrJRIMX21OU_UDnWU7NF-FOf3DCT_8sVQ"
url_list = get_urls_from_rss(rss_feed)
logger.info(str(url_list))



# Setting the locale to French
#locale.setlocale(locale.LC_TIME, 'fr_FR')

# Getting the current date
current_date = datetime.now()



# Formatting the date as "dd month yyyy"
formatted_date = current_date.strftime("%d %B %Y")
        
command = "A partir du texte suivant, \
        - rédige une section de script de podcast en français \
        - le contenu doit le plus complet possible par rapport au texte source mais etre traduit en français \
        - développe afin d'expliquer les termes techniques ou jargonneux à une audience grand public \
        Ne converse pas. Ne conclue pas. \
        Ne pas générer d'introduction ni de conclusion à cette section, juste le contenu. Ne pas commencer par Aujourd'hui nous allons parler de... Mais directement le contenu.\
        Si il n'y a pas d'article, ne pas dire qu'il n'y pas d'article, renvoyer une chaine vide.\
        Ne pas commencer par Voici la section ou voici le texte généré... Mais directement démarrer par le resultat. Respecter ces consignes strictement. "
     

responses = [lib_genpodcasts.process_url(command, url, model,"","") for url in url_list]
res = "<br><br>".join(responses)

text_veille = str(res.replace("```html", "")).replace("```", "")
logger.info("RESULTAT DE LA VEILLE \n\n\n")
logger.info(text_veille)
logger.info("FIN VEILLE \n\n\n")



prompt = """ Vous  trouverez dasn le context précédent, le texte surlequel baser le script du podcast à écrire."
Vous êtes chargé(e) d’écrire un script en français complet en moins de 4500 signes pour un podcast quotidien de revue de presse sur l'Intelligence Artificielle intitulé L'IA Aujourd’hui. Ce podcast doit être informatif, factuel et engageant, conçu pour un auditoire curieux mais non-expert. L’objectif est de fournir un contenu captivant et accessible tout en restant rigoureux.
TRES IMPORTANT : NE PAS DEMARRER LA REPONSE PAR UN MESSAGE COMME "Here's a plan to generate the script détaillant le plan de réponse.
Démarrer directement par le contenu du script généré et donc par "Bonjour..."

A partir des contenus suivant générer un script qui réponde aux caractéristiques suivantes :
- Structure du script :
  - Introduction :
    - Courte et percutante, introduire le podcast avec la phrase standard :  
      "Bonjour et bienvenue dans le podcast de l'IA par l’IA qui vous permet de rester à la page !"  
    - Suivre par une phrase résumant les sujets du jour, concise et dynamique :  
      "Aujourd’hui : [grandes thématiques du jour]."
  - Les grandes actualités du jour :  
    Développez chaque contenu fourni comme une actualité. TOUTES LES ACTULITES FOURNIES DOIVENT ETRE TRAITEES DANS LE SCRIPT. Les traiter, en incluant :
    - Contexte détaillé : origine, évolution du sujet.
    - Détails et implications : chiffres, exemples, conséquences.
    - Etre précis dans le compte rendu des infos. Pas d'information générique ou vague.
    - Évitez les actualités génériques ou redondantes, en privilégiant les informations originales et significatives.
    - être exhaustif dans la description de l'article (fournir les détails, les chiffres, les exemples, les conséquences cités dans l'article)
  - Transitions :  
    Utilisez des transitions naturelles entre les sujets, en assurant une narration fluide. Variez les styles pour éviter la répétition, mais restez sobre : pas d’abus de questions rhétoriques ou d’effets de style inutiles.
  - Conclusion :  
    Ne pas faire de récapitulatif court. Tout de suite après la dernière actualité, conclure avec la phrase standard :  
      "Voilà qui conclut notre épisode d’aujourd’hui. Merci de nous avoir rejoints, et n’oubliez pas de vous abonner pour ne manquer aucune de nos discussions passionnantes. À très bientôt dans L'IA Aujourd’hui !"

- Ton et style :
  - Utiliser un français journalistique, n'abuse pas des adjectifs, soit simple et direct
- Accessible mais rigoureux : Évitez un ton trop technique ou professoral. Expliquez les concepts sans les simplifier à outrance.
  - Engageant et fluide : Adoptez un style journalistique équilibré, dynamique mais sans excès d’emphase.
  - Informé et crédible : Appuyez-vous sur des faits en évitant les conjectures.
  - Sans redondance : Limitez les répétitions ou les apartés trop longs.
  - Unifier les thématiques : Lorsque possible, établissez des liens entre les sujets pour créer une narration cohérente et captivante.
  - N"utilise pas de titre pour chaque news.
  - N'insiste pas sur les questions rhétoriques pour chaque news et n'abuse pas des commentaires génériques relatifs à des questions, ethiques, philosophiques ou politiques liées à ces news. 
  - Contente toi de donner les faits mais détaille les bien.
  - inutile de citer auteur et source
  - Bannir les mots comme : "crucial", "important", "essentiel", "fondamental", "révolutionnaire", "extraordinaire", "incroyable", "exceptionnel", "fantastique", "génial", "fabuleux", "merveilleux", "formidable", "superbe", "extraordinaire", "époustouflant", "étonnant", "impressionnant", "phénoménal", "stupéfiant", "miraculeux", "prodigieux", "sensationnel", "sublime", "grandiose", "majestueux", "magnifique", "splendide", "éblouissant", "éclatant", "radieux", "rayonnant", "resplendissant", "scintillant", "étincelant", "chatoyant", "coloré", "vif", "éclatant" et éviter les superlatifs.

Objectif final : Produire un script détaillé de moins de 4500 signes (c'est trés important que le script fasse entre 4400 et 4500 signes), prêt à être lu, en intégrant TOUTES les actualités fournies de manière exhaustive et captivante.
TRES IMPORTANT : NE PAS DEMARRER LA REPONSE PAR UN MESSAGE COMME "Here's a plan to generate the script détaillant le plan de réponse.
Démarrer directement par le contenu du script généré et donc par "Bonjour à toutes et à tous..."
À partir de maintenant, réponds directement à ma question sans introduction.
"""

#prompt = "À partir du texte fourni, générer un script de podcast en français d'au moins 30000 signes pour 'L'IA aujourd'hui', présenté par Michel Lévy Provençal, avec l'introduction standard 'Bienvenue dans L'IA aujourd'hui : le podcast de l'IA par l'IA qui vous permet de rester à la page ! Je suis Michel Lévy Provençal, votre hôte' et la conclusion standard 'Voilà qui conclut notre épisode d'aujourd'hui. Merci de nous avoir rejoints et n'oubliez pas de vous abonner pour ne manquer aucune de nos discussions passionnantes. À très bientôt dans L'IA aujourd'hui !'. Adopter un style de revue de presse dynamique avec un ton journalistique engageant caractéristique de Michel Lévy Provençal. Chaque news doit être développée sur au moins 6000 signes, incluant contexte, détails et implications, en expliquant les termes techniques sans simplification excessive. Établir des liens pertinents entre les actualités pour créer une narration fluide. Ignorer les articles trop génériques ou manquant d'informations substantielles. Utiliser des transitions naturelles entre les sujets, des questions rhétoriques pour maintenir l'engagement, et un style narratif incluant le 'nous' inclusif. Le contenu doit être informatif et accessible, équilibrant faits techniques et analyse approfondie, en gardant toujours à l'esprit qu'il s'agit d'une revue de presse destinée à être écoutée."
#text_final = lib__agent_buildchronical.execute(prompt, '', text_veille, model)
# text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model, 16000)

model_synthese = "gpt-4o"
#model_synthese = "claude-3-5-sonnet-20241022"

if model_synthese=="google":
  text_final = lib_genpodcasts.call_google_llm(prompt, text_veille, "")
if model_synthese=="gpt-4o":  
  text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model_synthese, 16000)
if model_synthese=="o1-preview":
  text_final = lib_genpodcasts.call_llm(prompt, text_veille, "", model_synthese, 16000)
if model_synthese=="grok-2-latest":
  text_final = lib_genpodcasts.call_grok_llm(prompt, text_veille, "", model_synthese, 16000)
if model_synthese=="deepseek-chat":
  text_final = lib_genpodcasts.call_deepseek_llm(prompt, text_veille, "", model_synthese, 16000)
if model_synthese=="claude-3-5-sonnet-20241022":
  text_final = lib_genpodcasts.call_anthropic_llm(prompt, text_veille, "", model_synthese, 8192)


start_marker = "Bonjour à toutes et à tous"
end_marker = "À très bientôt dans L'IA Aujourd’hui !"
start_index = text_final.find(start_marker)
end_index = text_final.find(end_marker)

if start_index != -1 and end_index != -1:
  text_final = text_final[start_index:end_index + len(end_marker)]

logger.info("\n\n\n ----- RESULTAT DU SCRIPT DE PODCAST 1----- \n\n\n")
logger.info(text_final)
# prompt_net = "A partir de ce texte, retirer l'éventuelle introduction qui dit 'Here's the plan to generate the script' et renvoyer directement le script qui débute par 'Bonjour à toutes et à tous...' et qui finit par 'À très bientôt dans L'IA aujourd'hui !'."

# text_final = lib_genpodcasts.call_google_llm(prompt_net, text_final, "")

# logger.info("\n\n\n ----- RESULTAT DU SCRIPT DE PODCAST 2----- \n\n\n")
# logger.info(text_final)

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


titre = "L'IA aujourd'hui épisode du " + str(date.today())
text = text_final
audio = final_filename
email = "michel@brightness.fr"  # Remplacez 'destinataire' par 'email'
subtitle = "L'IA aujourd'hui : le podcast de l'IA par l'IA qui vous permet de rester à la page !"
# Appel de la fonction mailaudio
lib__agent_buildchronical.mailaudio(titre, audio, text, email)



# Conversion d'un fichier audio au format Acast
input_file = audio
output_file = input_file
#output_file = "datas/podcasts/datas_podcasts_final_podcast451932024-11-16_acast.mp3"

# Appel de la fonction de Conversion
#converted_file = convert_audio_to_acast_format(input_file, output_file)


#POST D'UN EPISODE SUR ACAST
logger.debug(f"Clé API utilisée : {ACAST_API_KEY}")
logger.info("\n\n\n")
headers = {
    "x-api-key": ACAST_API_KEY
}


# URL de l'API Acast
url = "https://open.acast.com/rest/shows/67328a919e7b27e0ac078578/episodes"
logger.info("Début de post de podcast")

# Charge utile
payload = {
    'title': titre,
    'subtitle': subtitle,
    'status': 'published',
    'summary': text,    
}


# Fichier audio à envoyer (fichier converti)
file_path = output_file

if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} n'existe pas ou le chemin est incorrect.")
else: 
    logger.info(f"Le fichier {file_path} existe.")
    logger.info("\n\n\n")
    
if os.path.getsize(file_path) == 0:
    raise ValueError(f"Le fichier {file_path} est vide.")
else:
    logger.info(f"Le fichier {file_path} existe et a une taille de {os.path.getsize(file_path)} octets.") 
    logger.info("\n\n\n")
# Préparez les fichiers à envoyer

files = [
    ('audio', (os.path.basename(file_path), open(file_path, 'rb'), 'audio/mpeg'))
]


logger.info("début d'envoi de podcast")
# Effectuez la requête
response = requests.post(url, headers=headers, data=payload, files=files)
logger.info("fin d'envoi de podcast")

# Affichez la réponse
logger.info(f"Statut : {response.status_code}")
logger.info("\n\n\n")
logger.info(f"En-têtes de la réponse : {response.headers}")
logger.info("\n\n\n")
logger.info(f"Réponse : {response.text}")



