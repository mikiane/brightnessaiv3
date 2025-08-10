


# ----------------------------------------------------------------------------
# Project: Semantic Search Module for the BrightnessAI project
# File:    llib__script_template_json.py
# 
# This library consists of several utility and execution functions designed to 
# process and handle task data for specific NLP tasks. These tasks can include 
# correction, drafting, paraphrasing, translation, summarization, and more, 
# in both English and French. The tasks are formatted as JSON or text files 
# and then processed using OpenAI's GPT-4.
# 
# Author:  Michel Levy Provencal
# Brightness.ai - 2023 - contact@brightness.fr
# ----------------------------------------------------------------------------

"""
Bibliothèque d’exécution de tâches LLM à partir de JSON/texte.
- Objectif: convertir des consignes en JSON, chercher du contexte, exécuter les prompts, streamer la sortie.
- Usage API: voir `alter_brain_api.py` (route /streamtasks).
"""

import json
from libs import lib__embedded_context
import os
import requests
import time
import openai
from urllib.parse import unquote
from queue import Queue
from datetime import *
from openai import OpenAI
import sys
from libs import lib__config as config
logger = config.logger

# Use configuration variables
DEFAULT_MODEL = config.DEFAULT_MODEL
model = DEFAULT_MODEL


####################################################################################################
# TOOL FUNCTIONS
####################################################################################################


# Fonction pour lire le fichier json
def read_json_file(file):
    with open(file, 'r') as f:
        data = json.load(f)
        #print(data)
    return data

# Fonction pour écrire dans un fichier json
def write_json_file(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

def json_to_txt(json_file, txt_file):
    # Lecture du fichier json
    tasks = read_json_file(json_file)

    # Ouvrir le fichier de sortie pour écrire
    with open(txt_file, 'w') as f:
        for task in tasks:
            prompt = tasks[task]['prompt']
            brain_id = tasks[task]['brain_id']
            input_data = tasks[task]['input_data']
            
            # Écrire les informations de la tâche dans le fichier texte
            f.write(f"Task: {task}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Brain_id: {brain_id}\n")
            f.write(f"Input Data: {input_data}\n")
            f.write("\n")  # ligne vide pour séparer les tâches







# Function that transforms a text file into a json file
def textfile_to_json(text_file, json_file):
    tasks = {}
    try:
        with open(text_file, 'r') as f:
            lines = f.readlines()
            task = None
            for line in lines:
                line = line.strip() 
                if line: 
                    try:
                        key, value = line.split(": ", 1)
                    except ValueError:
                        logger.error(f"Erreur de formatage sur la ligne : '{line}'. Ignoré.")
                        continue

                    if key == "Task":
                        task = value
                        tasks[task] = {}
                    else:
                        tasks[task][key.lower().replace(' ', '_')] = value
    except FileNotFoundError:
        logger.error(f"Le fichier '{text_file}' n'a pas été trouvé.")
        return
    
    try:
        with open(json_file, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError:
        logger.error(f"Erreur lors de l'écriture dans le fichier '{json_file}'.")

# Function that transforms a text into a json file
def text_to_json(text, json_file):
    tasks = {}
    lines = text.split('\n')
    task = None
    for line in lines:
        line = line.strip()
        if line: 
            if ": " not in line:
                logger.error(f"Ligne mal formatée : '{line}'. Ignoré.")
                continue

            try:
                key, value = line.split(": ", 1)
            except ValueError:
                logger.error(f"Erreur de formatage sur la ligne : '{line}'. Ignoré.")
                continue

            if key.strip() == "Task":
                task = value
                tasks[task] = {}
            else:
                tasks[task][key.lower().replace(' ', '_').strip()] = value.strip()
    
    try:
        with open(json_file, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError:
        logger.error(f"Erreur lors de l'écriture dans le fichier '{json_file}'.")



    
    


####################################################################################################
# SCRIPT EXECUTION FUNCTIONS
####################################################################################################

def request_llm(prompt, context, input_data, model=DEFAULT_MODEL):

    attempts = 0
    execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    while attempts < 10:
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.01,
                messages=[
                    {'role': 'user', 'content': execprompt},
                    {'role': 'system', 'content': system}
                ]
            )
            message = response.choices[0].message.content
            logger.info(str(datetime.now()) + " : " + "Réponse : " + str(message) + "\n\n")
            return message.strip()

        except Exception as e:
            error_code = type(e).__name__
            error_reason = str(e)
            attempts += 1
            logger.error(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans {str(attempts * 2)} secondes...")
            time.sleep(attempts * 2)

    logger.error("Erreur : Echec de la création de la completion après 10 essais")
    raise RuntimeError("LLM failure after 10 attempts")



 
def execute_tasks(tasks, model):
    
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    
    q = Queue()
    for task_name in tasks:
        q.put(task_name)

    while not q.empty():
        task_name = q.get()
        task = tasks[task_name]

        # input_data might be a task name, in which case we should use the result of that task
        input_data = unquote(task.get('input_data', ''))
        if input_data.startswith("task") and input_data in tasks and 'result' in tasks[input_data]:
            input_data = tasks[input_data]['result']

        prompt = unquote(task.get('prompt', ''))
        brain_id = unquote(task.get('brain_id', ''))
        
        model = model
        
        index_filename = "datas/" + brain_id + "/emb_index.csv"
        
        if brain_id.startswith("http://") or brain_id.startswith("https://"):
            url = brain_id
            index_filename= "datas/" + lib__embedded_context.build_index_url(url) + "/emb_index.csv"

        prompt, context, input_data = truncate_strings(prompt, '', input_data)
        
        # find context
        context = lib__embedded_context.find_context(prompt, index_filename, 3)
        
        
        if model==DEFAULT_MODEL:
            # truncate strings for gpt-4
            prompt, context, input_data = truncate_strings(prompt, context, input_data)
        else:
            # truncate strings for gpt-3.5-turbo
            prompt, context, input_data = truncate_strings(prompt, context, input_data, 4500)

        # prepare input data
        execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
        system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."
        attempts = 0
        
        # call openAI to get the streaming response 
        result = ''
        # ... [début de la fonction]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': execprompt}
                ],
                temperature=0.01,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content: 
                    text_chunk = chunk.choices[0].delta.content 
                    logger.debug(text_chunk)
                    yield text_chunk
                    result += str(text_chunk)

            logger.debug("\n\n")
            yield "\n\n"
            result += "\n\n"
            
        except Exception as e:  # catch general exceptions
            logger.error(f"Error: {e}")
            
        # Store the result in the task itself:
        task['result'] = result  

        # Update the input_data of tasks that depend on the completed task:
        for dependent_task_name, dependent_task in tasks.items():
            if 'input_data' in dependent_task and dependent_task['input_data'] == task_name:
                dependent_task['input_data'] = result

 
 
 
                
""" #################################################################################################### """ 
"""    
def request_llm_stream(prompt, context, input_data, model) :
    #load_dotenv(".env") # Load the environment variables from the .env file.
    #load_dotenv("/home/michel/extended_llm/.env") # Load the environment variables from the .env file.
    load_dotenv(DOTENVPATH)

    execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."

    attempts = 0
    while attempts < 3:  # essayer 3 fois avant d'abandonner
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': execprompt}
                ],
                temperature=0.01,
                stream=True
            )

            for chunk in response:
                if 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                    content = chunk['choices'][0]['delta']['content']
                    yield content

        except openai.error.OpenAIError as e:  # attraper les erreurs spécifiques à OpenAI
            attempts += 1
            print(f"Erreur OpenAI: {e}. Nouvel essai dans 5 secondes...")
            time.sleep(attempts * 2)
       
"""

def request_llm_stream(prompt, context, input_data, model):
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    execprompt = "Context : " + context + "\n" + input_data + "\n" + "Query : " + prompt
    system = "Je suis un assistant parlant parfaitement le français et l'anglais capable de corriger, rédiger, paraphraser, traduire, résumer, développer des textes."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': execprompt}
            ],
            temperature=0.01,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content: 
                content = chunk.choices[0].delta.content
                logger.debug(content)
                yield content
        

    except Exception as e:  # catch general exceptions
        logger.error(f"Erreur OpenAI: {e}.")


# tronuqer les chaînes pour éviter les erreurs de longueur
def truncate_strings(prompt, context, input_data, max_length=9000):
    # Définir la longueur maximale autorisée avec GPT4

    # Calculer la longueur actuelle de toutes les chaînes combinées
    total_length = len(prompt) + len(context) + len(input_data)

    # Si la longueur totale est déjà inférieure à la longueur maximale, aucune action n'est nécessaire
    if total_length <= max_length:
        return prompt, context, input_data

    # Sinon, commencer à tronquer les chaînes
    remaining_length = max_length - len(prompt) - len(context)

    # Si la longueur restante après avoir préservé `prompt` et `context` est négative, 
    # cela signifie que `prompt` et `context` seuls dépassent déjà la longueur maximale.
    # Dans ce cas, on tronque `context` pour s'adapter à la longueur maximale.
    if remaining_length < 0:
        context = context[:max_length - len(prompt)]
        input_data = ""
    else:
        # Sinon, tronquer `input_data` pour s'adapter à la longueur restante
        input_data = input_data[:remaining_length]

    return prompt, context, input_data

"""

# Fonction pour l'execution de taches
def exec_task(prompt, brain_id, input_data, model="gpt-4"):
    
    index_filename = "datas/" + brain_id + "/emb_index.csv"
    
    if model == "gpt-4":
        # Limitation des erreurs de longueur
        prompt, context, input_data = truncate_strings(prompt, '', input_data)
    else:
        # Limitation des erreurs de longueur
        prompt, context, input_data = truncate_strings(prompt, '', input_data, 4500)
        
    # recherche du contexte
    context = lib__embedded_context.query_extended_llm(prompt + input_data, index_filename, model)
    
    if model == "gpt-4":
        # Limitation des erreurs de longueur
        prompt, context, input_data = truncate_strings(prompt, context, input_data)
    else:
        # Limitation des erreurs de longueur
        prompt, context, input_data = truncate_strings(prompt, context, input_data, 4500)

    # Appel au LLM
    res = request_llm(prompt, context, input_data, model)

    return (res)



def execute_json(input_json_file, output_json_file, model="gpt-4"):
    # Lecture du fichier json
    tasks = read_json_file(input_json_file)
    
    for task in tasks:
        prompt = tasks[task].get('prompt', '')
        brain_id = tasks[task].get('brain_id', '')
        input_data = tasks[task].get('input_data', '')
        
        # Si la tâche dépend d'une autre tâche
        if input_data in tasks and 'result' in tasks[input_data]:
            # Utiliser le résultat de la tâche précédente
            input_data = tasks[input_data]['result']
        
        # Appeler la fonction execute la tache avec le contexte et obtenir le résultat
        result = exec_task(prompt, brain_id, input_data, model)

        # Ajouter le résultat à la tâche actuelle
        tasks[task]['result'] = result

    # Écriture du résultat dans le fichier json
    write_json_file(output_json_file, tasks)

"""

