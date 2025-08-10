"""
Génération de podcasts (texte → script → TTS) et intégrations LLM multi-fournisseurs
- Rassemble des utilitaires d’appel LLM (OpenAI, xAI, Deepseek, Google, Anthropic)
- Sert de brique pour `auto_genpodcast_*`
"""
import os
import json
import time
import requests
import google.generativeai as genai
import anthropic
from pydub import AudioSegment
from openai import OpenAI
from datetime import datetime, date

from libs import lib__agent_buildchronical
from libs import lib__transformers
from libs import lib__embedded_context
from libs import lib__config as config
logger = config.logger

# Variables de configuration
DESTINATAIRES_TECH = config.DESTINATAIRES_TECH
PODCASTS_PATH = config.PODCASTS_PATH
DEFAULT_MODEL = config.DEFAULT_MODEL
ACAST_API_KEY = config.ACAST_API_KEY
XAI_KEY = config.XAI_KEY
DEEPSEEK_KEY = config.DEEPSEEK_KEY
GEMINI_API_KEY = config.GEMINI_API_KEY
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY


def upload_and_get_public_url(service, file_path, file_name=None):
    """
    Uploads a file to Google Drive and returns its public URL.
    """
    if not file_name:
        file_name = file_path.split("/")[-1]
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, resumable=True)
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
        public_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        return public_url
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def process_url(command, url, model, site="", input_data=""):
    content = lib__agent_buildchronical.fetch_and_parse_urls(url)
    content = content.replace('\n', '')
    prompt = command + "\n ___ " + content + "\n ___ \n"
    res = lib__agent_buildchronical.execute(prompt, site, input_data, model)
    logger.info("URL traitée : " + url)
    return res


def call_llm(prompt, context, input_data, model=DEFAULT_MODEL, max_tokens=10000):
    attempts = 0
    execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais."
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    while attempts < 10:
        try:
            if model=="gpt-4o":
                response = client.chat.completions.create(
                    model=model,
                    temperature=0.01,
                    max_tokens=max_tokens,
                    messages=[
                        {'role': 'user', 'content': execprompt},
                        {'role': 'system', 'content': system}
                    ]
                )
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{'role': 'user', 'content': execprompt}]
                )
            message = response.choices[0].message.content
            return message.strip()
        except Exception as e:
            attempts += 1
            logger.error(f"Erreur : {type(e).__name__} - {e}. Nouvel essai dans {str(attempts * 2)} secondes...")
            time.sleep(attempts * 2)
    logger.error("Erreur : Echec de la création de la completion après 10 essais")
    raise RuntimeError("LLM failure")


def call_deepseek_llm(prompt, context, input_data, model=DEFAULT_MODEL, max_tokens=10000):
    execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais."
    client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": execprompt},
            {"role": "user", "content": system},
        ],
        stream=False
    )
    return response.choices[0].message.content.strip()


def call_grok_llm(prompt, context, input_data, model="grok-2-latest", max_tokens=8192):
    client = OpenAI(api_key=XAI_KEY, base_url="https://api.x.ai/v1")
    prompt_messages = [
        {"role": "system", "content": "Vous êtes un assistant."},
        {"role": "user", "content": "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt}
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=prompt_messages,
        max_tokens=max_tokens,
        temperature=0.2,
        top_p=1.0,
        n=1,
    )
    return str(completion.choices[0].message.content)


def call_google_llm(prompt, context, input_data, model="gemini-2.0-flash-thinking-exp-1219", max_tokens=8192):
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": max_tokens,
        "response_mime_type": "text/plain",
    }
    model_obj = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction="À partir de maintenant, réponds directement à ma question sans introduction.",
    )
    chat_session = model_obj.start_chat(history=[])
    response = chat_session.send_message("Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt)
    return response.text


def call_anthropic_llm(prompt, context, input_data, model="claude-3-5-sonnet-20241022", max_tokens=8192):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt}],
    )
    return message.content[0].text


def convert_audio_to_acast_format(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="mp3", parameters=["-ar", "44100", "-b:a", "128k"])
        logger.info(f"Fichier converti avec succès : {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Erreur lors de la conversion : {e}")
        return None
