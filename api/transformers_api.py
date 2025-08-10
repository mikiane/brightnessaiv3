# -*- coding: utf-8 -*-
'''
API Flask (transformers_api)
- Sommaire: routes de résumé de fichiers, transformation de texte, génération de podcast à partir de texte, et transcription audio (Whisper)
- Entrées sorties expliquées dans chaque route; configuration via `libs.lib__config`
'''

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from libs.lib__transformers import searchembedding
from libs import lib__transformers
import os
import uuid
from libs import lib__sendmail
from libs import lib__config as config
logger = config.logger

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
PODCASTS_PATH = config.PODCASTS_PATH
DEFAULT_MODEL = config.DEFAULT_MODEL

@app.route('/sumup', methods=['POST'])
def sumup():
    """Résumé d’un fichier texte uploadé puis envoi par e-mail du résultat."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    email = request.form.get('email')
    n = request.form.get('facteur')
    model = request.form.get('model', DEFAULT_MODEL)
    inputstring = uploaded_file.read().decode('utf-8')
    filename = lib__transformers.summarizelarge_chap(inputstring, str(email), n, model)
    lib__sendmail.mailfile(filename, email, uploaded_file.filename + "model:" + str(model))
    response = jsonify([{'id':1,'request':'summarize','answer':filename}])
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/transform', methods=['POST'])
def transform():
    """Transformation de texte selon une instruction (prompt) et envoi du fichier résultant par e-mail."""
    email = request.form.get('email')
    text = request.form.get('text')
    instruction = request.form.get('instruction')
    model = request.form.get('model', DEFAULT_MODEL)
    filename = lib__transformers.transform_chap(text, str(email), instruction, 1, model)
    lib__sendmail.mailfile(filename, email, str(instruction) + "model:" + str(model))
    response = jsonify([{'id':1,'request':'transform','answer':filename}])
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/podcast', methods=['POST'])
def podcast():
    """Génération audio (podcast) à partir d’un texte fourni puis envoi par e-mail du fichier audio."""
    text = request.form.get('text')
    email = request.form.get('email')
    filename = lib__transformers.synthesize_multi(text)
    lib__sendmail.mailfile(filename, email)
    response = jsonify([{'id':1,'request':text,'answer':filename}])
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/whisper', methods=['POST'])
def whisper():
    """Transcription audio (Whisper): upload d’un fichier audio, conversion, transcription et envoi du .txt par e-mail."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    clean_filename = audio_file.filename.replace(" ", "_")
    email = request.form.get('email')
    file_path = os.path.join(PODCASTS_PATH, clean_filename)
    audio_file.save(file_path)
    mp3_filename = lib__transformers.convert_to_mp3(file_path)
    output_filename = os.path.splitext(clean_filename)[0] + ".txt"
    transcript = lib__transformers.transcribe_audio(mp3_filename)
    lib__transformers.save_transcript(str(transcript), output_filename)
    logger.info(f"Transcription saved to {output_filename}")
    lib__sendmail.mailfile(output_filename, email)
    response = jsonify([{'id': 1, 'request': 'transform', 'answer': output_filename}])
    response.headers['Content-Type'] = 'application/json'
    return response