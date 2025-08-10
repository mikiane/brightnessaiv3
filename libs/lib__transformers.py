
'''
Transformations texte/audio (utilitaires)
- Fonctions: synthèse vocale (ElevenLabs), transformations LLM, transcription, conversions audio
- Utilisé par: `transformers_api.py`, scripts `auto_genpodcast_*`
'''
# Import the necessary libraries
import os
import subprocess
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
# Import elevenlabs de manière optionnelle
try:
    from elevenlabs import set_api_key as elevenlabs_set_api_key
except Exception:
    elevenlabs_set_api_key = None
from urllib.parse import unquote
from queue import Queue
# try:
#     from moviepy.editor import *
# except ImportError:
#    logger.warning("moviepy non installé - fonctionnalités vidéo désactivées")
from datetime import date
from bs4 import BeautifulSoup
import json
from num2words import num2words
import re
from libs import lib__sendmail
from openai import OpenAI
# Import centralized configuration
from libs import lib__config as config
logger = config.logger

# Use configuration variables directly
ELEVENLABS_API_KEY = config.ELEVENLABS_API_KEY
PODCASTS_PATH = config.PODCASTS_PATH
SENDGRID_KEY = config.SENDGRID_KEY
DEFAULT_MODEL = config.DEFAULT_MODEL
model = DEFAULT_MODEL

# Environment Variables
APP_PATH = config.APP_PATH
OPENAI_API_KEY = config.OPENAI_API_KEY
AWS_ACCESS_KEY = config.AWS_ACCESS_KEY
AWS_SECRET_KEY = config.AWS_SECRET_KEY
REGION_NAME = config.REGION_NAME


"""
# instantiate an Amazon Polly client
polly = boto3.client('polly', region_name=REGION_NAME,
                     aws_access_key_id=AWS_ACCESS_KEY,
                     aws_secret_access_key=AWS_SECRET_KEY)

# function to break down input text into smaller segments and then use Polly to generate speech
#### Synthèse avec Amazon Polly
def synthesize_multi_polly(inputtext):

    # define a maximum number of characters for each Polly API call
    max_chars = 2500
    segments = []

    # break down the input text into sentences
    sentences = inputtext.split('. ')
    current_segment = ''

    # iterate over each sentence and add to the current segment until the limit is reached
    for sentence in sentences:
        if len(current_segment) + len(sentence) + 1 <= max_chars:
            current_segment += sentence + '. '
        else:
            segments.append(current_segment)
            current_segment = sentence + '. '

    # add the last segment if it is not empty
    if current_segment:  
        segments.append(current_segment)

    # set up an output directory and a list to store paths to output files
    output_dir = APP_PATH + 'datas/'
    output_files = []

    # iterate over each segment
    for i, segment in enumerate(segments):
        print("Segment number :" + str(i))
        print("\n" + segment)
        
        # get the current time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current time is :", current_time)

        # prepare the text for the Polly API and make the request
        ssml_segment = "<speak><prosody rate=\"90%\">" + str(segment) + "</prosody></speak>"
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            VoiceId='Remi',
            TextType='ssml',
            Text=ssml_segment,
            LanguageCode='fr-FR',
            Engine='neural'
        )

        print("API response received")
        # get the current time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current time is :", current_time)
        audio_stream = response.get('AudioStream')
        audio_data = audio_stream.read()

        # generate a unique filename and save the audio data to a file
        filename = f"audiooutput_segment{i}.mp3"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'wb') as f:
            f.write(audio_data)

        # add the path to the output file to the list
        output_files.append(output_path)

    # concatenate all the audio files together
    combined_audio = pydub.AudioSegment.silent(duration=0)
    for output_file in output_files:
        segment_audio = pydub.AudioSegment.from_mp3(output_file)
        combined_audio += segment_audio

    # generate a filename for the final output file
    final_filename = "audiooutput" + str(random.randint(1, 10000)) + ".mp3"
    final_output_path = os.path.join(output_dir, final_filename)

    # save the combined audio to a file
    combined_audio.export(final_output_path, format='mp3')

    # return the path to the final output file
    return (output_dir + final_filename)

"""


def replace_numbers_with_text(input_string):
    
    # Remplacer les pourcentages
    percentages = re.findall(r'\d+%', input_string)
    for percentage in percentages:
        number = percentage[:-1]
        number_in_words = num2words(number, lang='fr')
        input_string = input_string.replace(percentage, f"{number_in_words} pour cent")
    
    # Remplacer les nombres
    numbers = re.findall(r'\b\d+\b', input_string)
    for number in numbers:
        number_in_words = num2words(number, lang='fr')
        input_string = input_string.replace(number, number_in_words)
    
    return input_string



def split_text(text, limit=1000):
    """
    This function splits the text into chunks of around 1000 characters. \n
    It splits before a newline character.
    """
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) <= limit:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk)
            current_chunk = line + "\n"

    # Append the last chunk
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks



##################################################################
### Function to convert text to speech with Eleven Labs API
def texttospeech(text, voice_id, filename):
    """
    This function calls the Eleven Labs API to convert text to speech
    """
    if not elevenlabs_set_api_key:
        raise RuntimeError("Le module elevenlabs ou set_api_key est indisponible. Vérifiez requirements et installation.")
    try:
        elevenlabs_set_api_key(str(ELEVENLABS_API_KEY))
        CHUNK_SIZE = 1024
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
        }

        data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.95,
            "similarity_boost": 0.2
            }
        }

        response = requests.post(url, json=data, headers=headers)

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    
    except requests.RequestException as e:
        logger.error(f"Failed to convert text to speech: {e}")
        return




def convert_and_merge(text, voice_id, final_filename):
    """
    This function splits the text, converts each chunk to speech and merges all the resulting audio files.
    """
    chunks = split_text(text)  # Assurez-vous que cette fonction est définie correctement
    filenames = []

    # Initialize combined as an empty AudioSegment
    combined = AudioSegment.empty()

    for i, chunk in enumerate(chunks):
        # Utiliser PODCASTS_PATH pour stocker les fichiers mp3 temporaires
        filename = os.path.join(str(PODCASTS_PATH), f"{str(i)}.mp3")
        logger.debug(filename)
        filenames.append(filename)
        texttospeech(chunk, voice_id, filename)  # Assurez-vous que cette fonction est définie correctement
        
        # Concatenate each audio segment
        audio_segment = AudioSegment.from_mp3(filename)
        combined += audio_segment

    # Save the final concatenated audio file
    combined.export(final_filename, format='mp3')

    # Delete temporary audio files
    for filename in filenames:
        os.remove(filename)


#### Synthèse avec Eleven Labs
#####
#voice_id = "DnF3PZl1PUQOKY4LvcUl" # MLP
#voice_id = "FL36qzLoYbdCLMM5R9rF" # MLP-PRO
#voice_id = "TxGEqnHWrfWFTfGW9XjX"  # Josh


def synthesize_multi(text, voice_id="Fgn8wInzqZU1U5EP2qp0"):
    # Use configuration from lib__config
    PODCASTS_PATH = config.PODCASTS_PATH

    # creation de l'audio
    final_filename = os.path.join(PODCASTS_PATH, "final_podcast" + str(randint(1, 10000)) + ".mp3")

    # gestion des intonations.
    convert_and_merge(replace_numbers_with_text(text), voice_id, final_filename)
    return (final_filename)


# Function to get the text embedding from OpenAI's API
def get_embedding(text, model="text-embedding-ada-002"):
    openai.api_key = OPENAI_API_KEY
    text = text.replace("\n", " ")  # Replaces newline characters with spaces
    return openai.Embedding.create(input = [text], engine=model)['data'][0]['embedding']  # Returns the embedding



# Function to search for a text within a local dataset using text embeddings
def searchembedding(text, filename):
    openai.api_key = OPENAI_API_KEY

    # Read the CSV file
    df = pd.read_csv(filename)

    # Convert the strings stored in the 'ada_embedding' column into vector objects
    df['ada_embedding'] = df.ada_embedding.apply(eval).apply(np.array)

    # Convert the search term into a vector
    searchvector = get_embedding(text, model='text-embedding-ada-002')

    # Create a new column using cosine_similarity to compare the searchvector with each row
    df['similarities'] = df.ada_embedding.apply(lambda x: np.dot(x, searchvector))

    # Sort the rows by similarity and keep the most similar one
    res = df.sort_values('similarities', ascending=False).head(1)

    # Set pandas option to display all columns
    pd.set_option('display.max_columns', None)

    # Check if the 'combined' column exists in the DataFrame
    if 'combined' in res.columns:
        # Check if the DataFrame is not empty
        if not res.empty:
            # Check if the index is of integer type
            if res.index.dtype == 'int64':
                # Return all records
                return '\n'.join(res['combined'].values)
            else:
                return "L'index du DataFrame n'est pas de type entier"
        else:
            return "Le DataFrame est vide"
    else:
        return "La colonne 'combined' n'existe pas dans le DataFrame"


"""
def mailfile(filename, destinataire, message=""):

    # Création de l'objet Mail
    message = Mail(
        from_email='contact@brightness.fr',
        to_emails=destinataire,
        subject='Le résultat du traitement' + message,
        plain_text_content='Votre demande a été traité.' + message)
    
    # Lecture du fichier à joindre
    with open(filename, 'rb') as f:
        data = f.read()

    # Encodage du fichier en base64
    encoded = base64.b64encode(data).decode()
    
    # Détermination du type MIME du fichier
    mime_type = mimetypes.guess_type(filename)[0]
    
    # Création de l'objet Attachment
    attachedFile = Attachment(
    FileContent(encoded),
    FileName(filename),
    FileType(mime_type),
    Disposition('attachment')
    )
    message.attachment = attachedFile

    # Tentative d'envoi de l'e-mail via SendGrid
    try:
        sg = SendGridAPIClient(SENDGRID_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
        
"""





# Function to split a large text into smaller blocks
def split_text_into_blocks(text, limit=4000):
    # Initialize variables
    blocks = []
    current_block = ""
    words = text.split()
    
    # Iterate over words
    for word in words:
        # Check if word fits in the current block
        if len(current_block + word) + 1 < limit:
            current_block += word + " "
        else:
            last_delimiter_index = max(current_block.rfind(". "), current_block.rfind("\n"))

            # Break block at the last complete sentence or newline
            if last_delimiter_index == -1:
                blocks.append(current_block.strip())
                current_block = word + " "
            else:
                delimiter = current_block[last_delimiter_index]
                blocks.append(current_block[:last_delimiter_index + (1 if delimiter == '.' else 0)].strip())
                current_block = current_block[last_delimiter_index + (2 if delimiter == '.' else 1):].strip() + " " + word + " "
    
    # Add the last block
    if current_block.strip():
        blocks.append(current_block.strip())

    return blocks

# Function to write blocks to a csv file
def write_blocks_to_csv(blocks, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for block in blocks:
            csvwriter.writerow([block])

# Function to generate a csv file from a string of text
def write_csv_from_string(text, filename):
    limit = 40000  # Limit for text blocks
    blocks = split_text_into_blocks(text, limit)  # Split text into blocks
    write_blocks_to_csv(blocks, filename)  # Write blocks to csv file




"""
# Function to summarize text
def transform(text, instruct, model="gpt-4"):
    api_key = OPENAI_API_KEY
    model = "gpt-4"
    if model=="gpt-4":
        limit = 10000  # Limit for text size
    else:
        limit = 5000
    prompt = instruct + "\n" + text[:limit] + ":\n"  # Construct the prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."

    # Try to make a request to the API
    attempts = 0
    while attempts < 10:
        try:
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            data = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt},
                    {'role': 'system', 'content': system}
                ]
            }
            response = requests.post(url, headers=headers, json=data)
            json_data = response.json()
            message = json_data['choices'][0]['message']['content']
            return message.strip()
        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 5 secondes...")
            time.sleep(5)

    print("Erreur : Echec de la création de la completion après 5 essais")
    sys.exit()

""" 



def transform(text, instruct, model=DEFAULT_MODEL):
    # Chargez votre clé API depuis la configuration centralisée
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    if model == DEFAULT_MODEL:
        limit = 90000  # Limite pour la taille du texte
    else:
        limit = 5000

    prompt = instruct + "\n" + text[:limit] + ":\n"
    system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."

    attempts = 0
    while attempts < 10:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )
            message = response.choices[0].message.content
            return message.strip()
        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            logger.error(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 5 secondes...")
            time.sleep(5)

    logger.error("Erreur : Échec de la création de la completion après 5 essais")
    raise RuntimeError("Transform failed after 5 attempts")



# Function to summarize a chapter of text
def transform_chap(text, prefix, instruct, n=3, model=DEFAULT_MODEL):
    model = DEFAULT_MODEL
    now = datetime.now()
    rand_str = str(now.strftime("%Y%m%d%H%M%S")) + "-"+ str(random.randint(0, 100))
    path = APP_PATH + "datas/"

    # Write input text to CSV
    input_f = path + "_" + prefix + "_input_" + rand_str +".csv"
    write_csv_from_string(text, input_f)

    # Summarize the text
    for j in range(1, n+1):
        # Update input filename
        if j > 1:
            input_f = output_f + "_" + str(j-1) + ".csv"

        with open(input_f, "r") as input_file:
            reader = csv.reader(input_file)
            # Update output filename
            output_f = path + "_" + prefix + "_output_" + rand_str
            with open(output_f + "_" + str(j) + ".csv", "w", newline="") as output_file:
                writer = csv.writer(output_file)
                rows_concatenated = []
                for row in reader:
                    rows_concatenated.append(row[0])
                    if (len(rows_concatenated) >= j) or (len(reader) == 0):
                        text = " ".join(rows_concatenated)
                        summary = transform(text, instruct, model)
                        writer.writerow([summary] + row[1:])
                        rows_concatenated = []

    # Write final summary to a text file
    outputxt = path + "_" + prefix + "_outputsummary_" + str(rand_str) + ".txt"
    with open(output_f + "_" + str(j) + ".csv", 'r') as csv_file, open(outputxt, 'w') as txt_file:
        csv_output = csv.reader(csv_file)
        for row in csv_output:
            txt_file.write(','.join(row) + '\n\n')

    return(outputxt)

# Function to split a large text into smaller blocks
def split_text_into_blocks(text, limit=4000):
    # Initialize variables
    blocks = []
    current_block = ""
    words = text.split()
    
    # Iterate over words
    for word in words:
        # Check if word fits in the current block
        if len(current_block + word) + 1 < limit:
            current_block += word + " "
        else:
            last_delimiter_index = max(current_block.rfind(". "), current_block.rfind("\n"))

            # Break block at the last complete sentence or newline
            if last_delimiter_index == -1:
                blocks.append(current_block.strip())
                current_block = word + " "
            else:
                delimiter = current_block[last_delimiter_index]
                blocks.append(current_block[:last_delimiter_index + (1 if delimiter == '.' else 0)].strip())
                current_block = current_block[last_delimiter_index + (2 if delimiter == '.' else 1):].strip() + " " + word + " "
    
    # Add the last block
    if current_block.strip():
        blocks.append(current_block.strip())

    return blocks

# Function to write blocks to a csv file
def write_blocks_to_csv(blocks, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for block in blocks:
            csvwriter.writerow([block])


# Function to summarize text
"""
def summarize(text, model='gpt-4'):
    model = "gpt-4"
    api_key = OPENAI_API_KEY
    if model=="gpt-4":
        limit = 10000  # Limit for text size
    else:
        limit = 5000
    prompt = "Texte : " + text[:limit] + "\nTache : Résumer le texte en respectant le style et le sens. \
        \nFormat : Un texte court dont le style et le sens sont conformes au texte original. \
        \nObjectif : Obtenir un résumé sans introduction particulière. \
        \nEtapes : Ne jamais mentionner que le texte produit est un résumé. \
        \n Le résumé : \
        \n"
    system = "Rôle : Etre un rédacteur en français spécialisé dans le résumé d’ouvrages."

    # Try to make a request to the API
    attempts = 0
    while attempts < 100000:
        try:
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            data = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt},
                    {'role': 'system', 'content': system}
                ]
            }

            response = requests.post(url, headers=headers, json=data)
            json_data = response.json()
            message = json_data['choices'][0]['message']['content']
            return message.strip()
        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 8 secondes...")
            time.sleep(1.1*attempts)

    print("Erreur : Echec de la création de la completion après x essais")
"""



def summarize(text, model=DEFAULT_MODEL):
    # Chargez votre clé API depuis la configuration centralisée
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    model = DEFAULT_MODEL
    if model == DEFAULT_MODEL:
        limit = 50000  # Limite pour la taille du texte
    else:
        limit = 5000

    prompt = "Texte : " + text[:limit] + "\nAction : Résumer le texte en français en respectant le style et le sens \
        Proposer un titre au résumé. \
        Ne JAMAIS mentionner le terme 'texte' ou 'résumé' dans le contenu produit \
        \n"
    system = "Rôle : Etre un rédacteur en français spécialisé dans le résumé d’ouvrages."

    attempts = 0
    while attempts < 100000:
        try:
            logger.debug("tentative résumé : " + str(attempts))
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
            logger.error(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans 8 secondes...")
            time.sleep(1.001 * attempts)

    logger.error("Erreur : Echec de la création de la completion après x essais")
    raise RuntimeError("Summarize failed after max attempts")



# Function to summarize large chapter
def summarizelarge_chap(text, prefix, n=3, model=DEFAULT_MODEL):
    model = DEFAULT_MODEL
    now = datetime.now()
    rand_str = str(now.strftime("%Y%m%d%H%M%S")) + "-"+ str(random.randint(0, 100))
    path = APP_PATH + "datas/"
    input_f = path + "_" + prefix + "_input_" + rand_str +".csv"
    output_f = path + "_" + prefix + "_output_" + rand_str

    # Write input to csv
    write_csv_from_string(text, input_f)
    j = 1

    # Summarize the text
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
                        summary = summarize(text, model)
                        writer.writerow([summary] + row[1:])
                        rows_concatenated = []
            j += 1

    # Write final summary to a text file
    outputxt = path + "_" + prefix + "_outputsummary_" + str(rand_str) + ".txt"
    inputcsv = output_f + "_" + str(j-1) + ".csv"
    with open(inputcsv, 'r') as csv_file, open(outputxt, 'w') as txt_file:
        csv_output = csv.reader(csv_file)
        for row in csv_output:
            txt_file.write(','.join(row) + '\n\n')

    return(outputxt)




#Audio to text conversion




def convert_to_mp3(input_file):
    ext = os.path.splitext(input_file)[-1].lower()[1:]  # Extrait l'extension sans le point
    
    if ext not in ["m4a", "wav", "mp3", "mp4", "mov"]:
        raise ValueError(f"Extension de fichier non prise en charge : {ext}")
    
    if ext == "mp3":
        return os.path.join(PODCASTS_PATH, os.path.basename(input_file))
    
    output_filename = os.path.join(PODCASTS_PATH, os.path.basename(input_file).rsplit('.', 1)[0] + ".mp3")

    if ext == "m4a":
        ## Solution avec Soundconverter
        # Convert m4a to wav
        temp_wav = os.path.join(PODCASTS_PATH, "temp.wav")
        #command_to_wav = ["xvfb-run", "soundconverter", "-b", "-m", "audio/x-wav", "-i", input_file, "-o", temp_wav]
        command_to_wav = ["soundconverter", "-b", "-s", ".wav", "-m", "audio/x-wav", "-i", input_file, "-o", temp_wav]
        subprocess.run(command_to_wav)

        # Convert wav to mp3
        command_to_mp3 = ["soundconverter", "-b", "-s", ".mp3", "-m", "audio/mpeg", "-i", temp_wav, "-o", output_filename]
        #command_to_mp3 = ["xvfb-run", "soundconverter", "-b", "-m", "audio/mpeg", "-i", temp_wav, "-o", output_filename]
        subprocess.run(command_to_mp3)

        # Optionally delete the temporary wav 

        
    if ext == "wav":
        command = ["/usr/bin/ffmpeg", "-y", "-i", input_file, output_filename]
        subprocess.run(command, check=True)
        
    if ext == "mp4" or ext == "mov":
        command = ["/usr/bin/ffmpeg", "-y", "-i", input_file, "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", output_filename]
        subprocess.run(command)
        
    return output_filename

# Configurez votre clé API OpenAI

"""
def transcribe_audio(audio_filename):
    with open(audio_filename, "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    transcript = response.get('text')
    return transcript
"""
    

def transcribe_audio(audio_filename):

    # Initialiser le client OpenAI
    api_key = config.OPENAI_API_KEY
    client = OpenAI(api_key=api_key)

    # Ouvrir le fichier audio en mode binaire
    audio_file = open(audio_filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text"
    )
    
    # Récupérer et retourner la transcription
    return transcript

    
def save_transcript(transcript, output_filename):
    with open(output_filename, "w", encoding="utf-8") as output_file:
        output_file.write(str(transcript))


