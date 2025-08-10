# -*- coding: utf-8 -*-

import anthropic
import os

# Import centralized configuration
from libs import lib__config as config


# Environment Variables
ELEVENLABS_API_KEY = config.ELEVENLABS_API_KEY
PODCASTS_PATH = config.PODCASTS_PATH
SENDGRID_KEY = config.SENDGRID_KEY
OPENAI_API_KEY = config.OPENAI_API_KEY
AWS_ACCESS_KEY = config.AWS_ACCESS_KEY
AWS_SECRET_KEY = config.AWS_SECRET_KEY
REGION_NAME = config.REGION_NAME
ANTHROPIC_API_KEY = config.ANTHROPIC_API_KEY

# Assurez-vous d'avoir défini votre clé API comme variable d'environnement
api_key = ANTHROPIC_API_KEY



def generate_chat_completion_anthropic(consigne, texte, model="claude-3-opus-20240229", temperature=0):
# Construct the prompt from the given consigne and texte

    prompt = f"{anthropic.HUMAN_PROMPT} {consigne} : {texte}{anthropic.AI_PROMPT}"
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Create a stream completion using the Anthropic API
    completion = client.messages.stream(
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature
    )

    # Iterate over the stream completions and yield the results
    with completion as stream:
        for text in stream.text_stream:
            yield text
            
            


###### OLD VERSIONS OF API CALLS #########

def generate_chat_completion_anthropic_v2(consigne, texte, model="claude-3-opus-20240229"):
    

    # Construct the prompt from the given consigne and texte
    prompt = f"{anthropic.HUMAN_PROMPT} {consigne} : {texte}{anthropic.AI_PROMPT}"

    # Create an Anthropic client
    client = anthropic.Anthropic()
    
    # Create a stream completion using the Anthropic API
    stream = client.completions.create(
        prompt=prompt,
        model=model,
        stream=True,
        temperature=0,
        # Set any other desired parameters here, for example:
        max_tokens_to_sample=99000
    )

    # Iterate over the stream completions and yield the results
    for completion in stream:
        yield completion.completion
        
        

def generate_chat_completion_anthropic_request(consigne, texte, model="claude-3-opus-20240229"):
    # Construct the prompt from the given consigne and texte
    prompt = f"{anthropic.HUMAN_PROMPT} {consigne} : {texte}{anthropic.AI_PROMPT}"
    
    # Set the API endpoint URL
    url = "https://api.anthropic.com/v1/messages"
    
    # Set the headers
    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "messages-2023-12-15",
        "content-type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY
    }
    
    # Set the request data
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 99000,
        "stream": True
    }
    
    # Send the POST request to the API endpoint
    response = requests.post(url, headers=headers, json=data, stream=True)
    
    # Iterate over the stream completions and yield the results
    for line in response.iter_lines():
        if line:
            yield line.decode('utf-8')

