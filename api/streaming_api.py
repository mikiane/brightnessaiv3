# -*- coding: utf-8 -*-
'''
Application Flask de chat IA (SSE en streaming et réponse standard)
- Objet: Expose deux routes `/stream_chat` (flux texte continu) et `/stream_chat_temp` (réponse simple)
- Entrées: JSON { consigne, texte, system (opt), model (opt), temperature (opt) }
- Sorties: texte brut (Content-Type: text/plain)
- Dépendances: `libs.lib__llm_models.llm_manager` pour l’appel unifié LLM, `libs.lib__config` pour la config
'''

from libs.lib__llm_models import llm_manager
from flask import Flask, Response, request, jsonify
from libs import lib__config as config
from libs.lib__auth import require_auth, setup_cors, add_security_headers
import os
from datetime import datetime

logger = config.logger
DEFAULT_MODEL = config.DEFAULT_MODEL

app = Flask(__name__)
# Configuration CORS sécurisée
setup_cors(app)

def log_to_file(ip_address, request_data, response_text, log_file="docs/traces.txt"):
    """
    Enregistre les requêtes et réponses dans un format ultra lisible.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Date: {timestamp}
IP: {ip_address}

INPUT:
  Consigne: {request_data.get('consigne', '')}
  Texte: {request_data.get('texte', '')}
  System: {request_data.get('system', '')}
  Model: {request_data.get('model', '')}

OUTPUT:
{response_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

# Ajouter les headers de sécurité à toutes les réponses
@app.after_request
def after_request(response):
    return add_security_headers(response)

@app.route('/stream_chat', methods=['POST'])
@require_auth
def stream_chat():
    """
    Route de chat en streaming.
    - But: renvoyer la génération au fil de l'eau (SSE côté client)
    - Entrée: JSON avec `consigne` (instruction), `texte` (contexte), `model` (optionnel)
    - Retour: flux texte progressif (text/plain)
    """
    data = request.get_json()
    consigne = data.get('consigne')
    texte = data.get('texte')
    system = data.get('system', '')
    model = data.get('model', DEFAULT_MODEL)
    from urllib.parse import unquote
    consigne = unquote(consigne)
    texte = unquote(texte)
    logger.info(f"STREAM completion: model={model}")
    
    # Récupérer l'IP du client
    client_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'Unknown')
    
    # Préparer les données de requête pour le log
    request_data = {
        'consigne': consigne,
        'texte': texte,
        'system': system,
        'model': model
    }
    
    # Générer la réponse et la capturer
    response_generator = llm_manager.generate_chat(consigne, texte, system='', model=model, temperature=0)
    
    # Capturer la réponse complète pour le logging
    full_response = ""
    
    def generate_and_log():
        nonlocal full_response
        for chunk in response_generator:
            full_response += chunk
            yield chunk
        
        # Logger après la génération complète
        log_to_file(client_ip, request_data, full_response)
    
    return Response(generate_and_log(), content_type='text/plain')

@app.route('/stream_chat_temp', methods=['POST'])
@app.route('/chat', methods=['POST'])  # Alias pour rétrocompatibilité
@require_auth
def stream_chat_temp():
    """Route de chat standard (réponse unique).
    Accessible via /stream_chat_temp ou /chat (rétrocompatibilité).
    """
    data = request.get_json()
    consigne = data.get('consigne')
    texte = data.get('texte')
    system = data.get('system', '')
    model = data.get('model', DEFAULT_MODEL)
    temperature_str = data.get('temperature', '0').replace(',', '.') or '0'
    temperature = float(temperature_str)
    from urllib.parse import unquote
    consigne = unquote(consigne)
    texte = unquote(texte)
    logger.info(f"CHAT: model={model}, temperature={temperature}")
    
    # Récupérer l'IP du client
    client_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'Unknown')
    
    # Préparer les données de requête pour le log
    request_data = {
        'consigne': consigne,
        'texte': texte,
        'system': system,
        'model': model,
        'temperature': temperature
    }
    
    # Générer la réponse et la capturer
    response_generator = llm_manager.generate_chat(consigne, texte, system, model, temperature)
    
    # Capturer la réponse complète pour le logging
    full_response = ""
    
    def generate_and_log():
        nonlocal full_response
        for chunk in response_generator:
            full_response += chunk
            yield chunk
        
        # Logger après la génération complète
        log_to_file(client_ip, request_data, full_response)
    
    return Response(generate_and_log(), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
