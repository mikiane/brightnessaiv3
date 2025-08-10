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
from flask_cors import CORS
from libs import lib__config as config
logger = config.logger
DEFAULT_MODEL = config.DEFAULT_MODEL

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/stream_chat', methods=['POST'])
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
    return Response(llm_manager.generate_chat(consigne, texte, system='', model=model, temperature=0), content_type='text/plain')

@app.route('/stream_chat_temp', methods=['POST'])
def stream_chat_temp():
    """Route de chat standard (réponse unique)."""
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
    return Response(llm_manager.generate_chat(consigne, texte, system, model, temperature), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
