import lib__transformers
# Import the necessary libraries
import os
import subprocess
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import openai
import boto3
import tempfile
import random
from random import randint
from datetime import datetime
import pydub
from pydub import AudioSegment
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import mimetypes
import time
import sys
import csv
import requests
import time
import csv
from elevenlabs import set_api_key
from urllib.parse import unquote
from queue import Queue
from moviepy.editor import *
from datetime import date
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from bs4 import BeautifulSoup
import json
from num2words import num2words
import re
import lib__sendmail
from openai import OpenAI
import openai
import anthropic
from anthropic import HUMAN_PROMPT, AI_PROMPT
import os
from dotenv import load_dotenv



model="gpt-4"
# Charger les variables d'environnement depuis le fichier .env
load_dotenv('.env')

#model = "gpt-3.5-turbo"
#load_dotenv(".env")  # Load the environment variables from the .env file.
#load_dotenv("/home/michel/extended_llm/.env")  # Load the environment variables from the .env file.
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
PODCASTS_PATH = os.environ.get("PODCASTS_PATH")
SENDGRID_KEY = os.environ.get("SENDGRID_KEY")
# Environment Variables
SENDGRID_KEY = os.environ['SENDGRID_KEY']
#APP_PATH = os.environ['APP_PATH']
APP_PATH = "/Users/michel/Dropbox (Compte personnel)/1-DEVELOPPEMENTS/Git/brightnessaiv2/"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
REGION_NAME = os.environ['REGION_NAME']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']


def guiz(text, model='gpt-4-turbo-preview'):
    # Chargez votre clé API depuis une variable d'environnement ou directement
    client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    model = "gpt-4-turbo-preview"
    if model == "gpt-4-turbo-preview":
        limit = 20000  # Limite pour la taille du texte
    else:
        limit = 10000

    prompt = "Texte : " + text[:limit] + "\nTache : A partir du texte suivant générer un QCM comprenant 3 questions différentes sur le contenu du texte. \
        \nFormat : Le QCM doit etre en Français. Chaque question, doit proposer 4 réponses. 3 fausses. Une juste. La réponse juste doit etre suivie de la mention (Bonne réponse) \
        \nAttention, il faut que la question puisse être claire et autoporteuse (par exemple elle ne doit pas etre formulée de la manière suivante : quelle information le texte expose ?). Il est TRICTEMENT INTERDIT de mentionner l'expression 'dans le texte' ou 'dans le contenu'. Il faut TOUJOURS que la question puisse etre assez complete et précise pour qu'on puisse y répondre sans avoir accès au texte à partir du quel la question a été générée. \
        \Style : Respecter le niveau de complexité, le ton et le style du texte source. \
        \n Le QCM : \
        \n"
    system = "Rôle : Etre un rédacteur en français spécialisé dans la création de QCM en français à partir de textes."

    attempts = 0
    while attempts < 100000:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": system}
                ]
            )
            message = response.choices[0].message.content
            return message.strip()
        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 8 secondes...")
            time.sleep(1.1 * attempts)

    print("Erreur : Echec de la création de la completion après x essais")
    sys.exit()


# Function to generate a csv file from a string of text
def write_csv_from_string(text, filename):
    limit = 12000  # Limit for text blocks - taille des blocs
    blocks = lib__transformers.split_text_into_blocks(text, limit)  # Split text into blocks
    lib__transformers.write_blocks_to_csv(blocks, filename)  # Write blocks to csv file


# Function to summarize large chapter
def gen_quiz(text):
    n=1
    prefix = "quiz"
    model = "gpt-4"
    now = datetime.now()
    rand_str = str(now.strftime("%Y%m%d%H%M%S")) + "-"+ str(random.randint(0, 100))
    path = APP_PATH + "datas/"
    input_f = path + "_" + prefix + "_input_" + rand_str +".csv"
    output_f = path + "_" + prefix + "_output_" + rand_str


    # Write input to csv
    lib__transformers.write_csv_from_string(text, input_f)
    j = 1

    while j <= int(n):
        if j > 1:
            input_f = output_f + "_" + str(j-1) + ".csv"

        with open(input_f, "r") as input_file_count:
            reader = csv.reader(input_file_count)
            lines = sum(1 for _ in reader)

            if lines < j:
                break

        with open(input_f, "r") as input_file:
            reader = csv.reader(input_file)
            with open(output_f + "_" + str(j) + ".csv", "w", newline="") as output_file:
                writer = csv.writer(output_file)
                rows_concatenated = []
                for row in reader:
                    lines -= 1
                    rows_concatenated.append(row[0])

                    if (len(rows_concatenated) >= j) or (lines==0):
                        text = " ".join(rows_concatenated)
                        summary = guiz(text, model)
                        writer.writerow([summary] + row[1:])
                        rows_concatenated = []
            j += 1

    # Write final summary to a text file
    outputxt = path + "_" + prefix + "_outputquiz_" + str(rand_str) + ".txt"
    inputcsv = output_f + "_" + str(j-1) + ".csv"
    with open(inputcsv, 'r') as csv_file, open(outputxt, 'w') as txt_file:
        csv_output = csv.reader(csv_file)
        for row in csv_output:
            txt_file.write(','.join(row) + '\n\n')

    return(outputxt)


def read_file(file_path):
    """Fonction pour lire le contenu d'un fichier."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()



def cut_blocks(text, max_length=10000):    
# cut_blocks : fonction qui prend un texte et le divise en blocs de 10 000 caracteres environ. Ne pas couper les phrases. 
# la fonction renvoie une liste de blocs.
    """
    Divides a text into blocks of approximately max_length characters.
    Tries to avoid cutting sentences in the middle and prefers to cut at paragraph ends.

    :param text: The input text to be divided.
    :param max_length: The maximum length of each block.
    :return: A list of text blocks.
    """
    # Splitting the text into paragraphs
    paragraphs = text.split('\n')

    blocks = []
    current_block = ""

    for paragraph in paragraphs:
        # Check if adding this paragraph exceeds the max length
        if len(current_block) + len(paragraph) > max_length:
            # Add the current block to blocks if it's not empty
            if current_block:
                blocks.append(current_block)
                current_block = ""

            # If the paragraph itself is longer than the max length, split it further
            while len(paragraph) > max_length:
                # Find the last sentence end in the allowed length
                cut_index = paragraph.rfind('. ', 0, max_length)
                if cut_index == -1:
                    # If no sentence end is found, default to the max length
                    cut_index = max_length

                # Add the split paragraph part to the blocks
                blocks.append(paragraph[:cut_index + 1])
                # Remove the added part from the paragraph
                paragraph = paragraph[cut_index + 1:].lstrip()

        # Add the (remaining part of the) paragraph to the current block
        current_block += paragraph + '\n'

    # Add the last block if it's not empty
    if current_block:
        blocks.append(current_block)

    return blocks

# Commenting out the function call for now
# text_example = "Your very long text here..."
# print(cut_blocks(text_example))

# Code pour transformer une chaîne de caractères en liste de titres
def string_to_list(input_str):
    # Trouver la partie de la chaîne entre les crochets
    start = input_str.find('[') + 1
    end = input_str.find(']', start)
    list_str = input_str[start:end]

    # Séparer les titres et les nettoyer
    titles = [title.strip() for title in list_str.split(',')]

    return titles

# Exemple d'utilisation
# input_str = "list : [titre 1, titre2, titre3]"
# result = string_to_list(input_str)
# print(result)  # Doit afficher ['titre 1', 'titre2', 'titre3']


# find_chap : fonction qui prend un texte et appelle un LLM pour qu'il extrait les titres de chapitre qui le constituent. 
# la fonction renvoie une liste de titres de chapitre.







def find_chap(text):
    
    # ANTROPIC
    
    model = "claude-2.1"
    consigne = "A partir de ce texte, trouver les titres des parties ou chapitres. Renvoyer comme réponse un tableau au format python : [['titre 1', 'titre2',..., 'titren']]]]"

    # Construction du prompt à partir de la consigne et du texte
    prompt = f"{HUMAN_PROMPT} {consigne} : {text}{AI_PROMPT}"

    # Création d'un client Anthropic
    
    response = anthropic.Anthropic().completions.create(
    model=model,
    max_tokens_to_sample=10000,
    prompt=prompt,
    temperature = 0,
    )
    print(response)
    result = response.completion.strip()
    list_of_chap = string_to_list(result)
    print(list_of_chap)
    return list_of_chap
    
    
    
    # OPENAI
    # Chargez votre clé API depuis une variable d'environnement ou directement
    
    """
    client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    model = "gpt-4-1106-preview"

    prompt = "A partir de ce texte, extraire les titres de chapitre qui le constituent. La réponse que tu fournis doit etre un tableau au format python : [['titre 1', 'titre2',..., 'titren']]]]"
    system = "Rôle : tu es un lecteur interpreteur. Toutes les réponses que tu apportes concenent les titres exacts que tu extraits d'un texte. Tes réponses sont tujours au format python : [['titre 1', 'titre2',..., 'titren']]]]."
    attempts = 0
    while attempts < 100000:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt + " :" + text},
                    {"role": "system", "content": system}
                ]
            )
            message = response.choices[0].message.content
            
            result = message.strip()
            list_of_chap = string_to_list(result)
            print(list_of_chap)
            return list_of_chap 
        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 8 secondes...")
            time.sleep(1.1 * attempts)

    print("Erreur : Echec de la création de la completion après x essais")
    sys.exit()
    
"""    



# extract_chap : fonction qui prend un texte et une liste de titres de chapitre en format tabelau (['titre 1', 'titre2', 'titre3']) et extrait le texte de chaque chapitre.
# pour ce faire la fonction renvoie un tableau comprenant : titre, blocs de texte
# les blocs de textes sont etxraits en procédant comme suit : 
# - on cherche le titre dans le texte
# - on cherche le titre suivant dans le texte
# - on extrait le texte entre les deux titres
# - on recommence avec le titre suivant
# - quand on arrive au dernier titre on extrait le texte jusqu'à la fin du texte
def extract_chap(text, chapter_titles):
    chapters = []
    start = 0

    for i in range(len(chapter_titles)):
        # Trouver le début du chapitre actuel
        start = text.find(chapter_titles[i], start)

        # Si le titre n'est pas trouvé, passer au suivant
        if start == -1:
            continue

        # Trouver le début du chapitre suivant (ou la fin du texte)
        if i < len(chapter_titles) - 1:
            end = text.find(chapter_titles[i + 1], start)
            if end == -1:
                end = len(text)
        else:
            end = len(text)

        # Extraire le texte du chapitre
        chapter_text = text[start:end].strip()
        chapters.append((chapter_titles[i], chapter_text))

        # Mettre à jour le point de départ pour la recherche du chapitre suivant
        start = end

    return chapters

# Exemple d'utilisation
# text = "Chapitre 1: Introduction... Chapitre 2: Développement... Conclusion..."
# chapter_titles = ["Chapitre 1", "Chapitre 2", "Conclusion"]
# chapters = extract_chap(text, chapter_titles)
# for title, content in chapters:
#     print(f"Titre: {title}\nTexte: {content}\n")


# extract_chap_content : fonction qui 
# 1. prend un texte en entrée
# 2. appelle cut_blocks. Ce qui renvoie la liste des blocs de texte
# 3. appel de find_chap sur chaque bloc de texte. Pour chaque appel on récupère la liste des titres de chapitre et on les ajoute à une liste de titres de chapitre
# 4. appel de extract_chap sur le texte et la liste de titres de chapitre. Ce qui renvoie un tableau comprenant : titre de chapitre, blocs de texte

def extract_chap_content(text, block_size=10000):
    # Initialize an empty dictionary to store chapters and their contents
    chapters = []

    # Split the text into blocks
    blocks = cut_blocks(text, block_size)

    # Process each block
    for block in blocks:
        # Find chapter titles in the block
        chap_list = find_chap(block)

        # Extract chapters and their contents
        chapters.extend(extract_chap(block, chap_list))

    # Return the dictionary containing all chapters and their contents
    return chapters

# The function calls for `cut_blocks`, `find_chap`, and `extract_chap` are commented out
# as their implementations are not provided here


# summarize_chap : fonction qui prend un texte et un titre de chapitre en entrée et renvoie un résumé du chapitre en question

#summarize_all : fonction qui prend un texte en entrée et renvoie un résumé de tous les chapitres du texte en utilisant summarize_chap

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

"""
file_path = "/Users/michel/Dropbox (Compte personnel)/1-DEVELOPPEMENTS/Git/brightnessaiv2/sapienssample.txt"
text = read_file(file_path)
chapters = extract_chap_content(text, block_size=10000)
chapters
"""


prompt = "Imagine une breaking news écrite (type depeche AFP ou Reuters mais rédigée correctement) possible entre 2025 et 2030 qui relate un événement marquant (le début d’un conflit, une election surprise, un accident, la sortie d’une nouvelle technologie, un événement critique sanitaire, économique, financier, environnemental, politique…). L'événement doit etre critique. C'est une crise majeure. Soit très précis quand tu relates l’événement que tu inventes. Tu peux utiliser les 4W du journalisme What, Who, When, Where comme structure, mais rédige le texte comme une courte dépeche d'agence. Conclue par les repercussion que cet événement peut avoir sur un secteur économique particulier. Choisis un seul. A chaque fois que tu fais cet exercice de création, choisis un nouveau type d’événement, un nouveau lieu une nouvelle problématique, un nouveau secteur impacté. Cite toujours la date. Le format doit être un article court. Limite la depeche à 240 caractères."
system = "Rôle : Etre un rédacteur d'articles fictifs destinés à alimenter un serious game, une simulation. Le redacteur s'appuie sur des tendances et des faits réels pour rendre l'article le plus crédible possible. Il ecrit exlusivement en français."
client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
model = "gpt-4-turbo-preview"

attempts = 0

while attempts < 50:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": system}
            ]
        )
        result = response.choices[0].message.content

        output = result.strip()
        print(output)

        # Ouvrir, écrire et fermer le fichier à chaque itération
        with open('output.txt', 'a') as file:
            file.write(output + "\n\n\n______________________________________________________________________________________________\n\n\n")
        
    except Exception as e:
        error_code = type(e).__name__
        error_reason = str(e)
        attempts += 1
        print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 8 secondes...")
        time.sleep(1.1 * attempts)

if attempts >= 50:
    print("Erreur : Echec de la création de la completion après 50 essais")
    sys.exit()



