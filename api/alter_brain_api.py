
# ----------------------------------------------------------------------------
# API Flask Alter Brain
# - Construire un index vectoriel à partir d’un zip ou d’un dossier envoyé (buildindex)
# - Rechercher du contexte dans un index existant (searchcontext)
# - Exécuter un script de tâches en streaming textuel (streamtasks)
# ----------------------------------------------------------------------------

from libs import lib__embedded_context
from flask import Flask, request, jsonify, Response
from libs.lib__auth import require_auth, setup_cors, add_security_headers
import os
import time
from zipfile import ZipFile
from libs import lib__sendmail
from libs import lib__script_tasks
import random
from libs import lib__config as config
logger = config.logger
from libs import lib_vectorize_context
from libs.lib__llm_models import extract_context
DEFAULT_MODEL = config.DEFAULT_MODEL

base_folder = "datas/"
app = Flask(__name__)
# Configuration CORS sécurisée
setup_cors(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Ajouter les headers de sécurité
@app.after_request
def after_request(response):
    return add_security_headers(response)

@app.route('/buildindex', methods=['POST'])
@require_auth
def handle_file():
    """
    Construire un index de documents.
    - Upload: zip ou fichier(s) → création d’un dossier daté
    - Indexation: lance `build_index` sur le dossier
    - Retour: `brain_id` (identifiant de l’index)
    """
    logger.info("dans buildindex")
    if 'file' not in request.files:
        logger.warning("pas de fichier fourni")
        return jsonify({'error': 'No file provided'}), 400
    uploaded_file = request.files['file']
    email = request.form.get('email')
    logger.info("email à utiliser pour envoyer le brain id : " + str(email))
    if uploaded_file.filename == '':
        logger.warning("nom de fichier vide")
        return jsonify({'error': 'No file provided'}), 400
    base_name = os.path.splitext(uploaded_file.filename)[0]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    folder_name = f"{base_folder}{base_name}_{timestamp}/"
    logger.info("creation du folder_name s'il n'existe pas : " + folder_name)
    os.makedirs(folder_name, exist_ok=True)
    if uploaded_file.filename.endswith('.zip'):
        with ZipFile(uploaded_file, 'r') as zip_ref:
            logger.info("extraction zip")
            zip_ref.extractall(folder_name)
    else:
        file_path = os.path.join(folder_name, uploaded_file.filename)
        uploaded_file.save(file_path)
        logger.info("recuperation fichier unique")
    logger.info("folder_name for build_index : " + folder_name)
    lib__embedded_context.build_index(folder_name)
    brain_id = base_name + "_" + timestamp
    res = [{'id':1, 'request':'buildindex', 'answer':brain_id}]
    response = jsonify(res)
    response.headers['Content-Type'] = 'application/json'
    logger.info("brain_id : " + str(brain_id))
    lib__sendmail.mailfile(None, email, ' Votre index est prêt. Son brain_id est : ' + str(brain_id))
    return(response)

@app.route('/searchcontext', methods=['POST'])
@require_auth
def handle_req():
    """
    Rechercher du contexte pertinent dans un index existant.
    - Entrée form: `request` (texte), `brain_id` (ou URL), `model` (optionnel)
    - Retour: fragments de contexte trouvés (JSON)
    """
    text = request.form.get('request')
    index = request.form.get('brain_id')
    model = request.form.get('model', DEFAULT_MODEL)
    index_filename = "datas/" + index + "/emb_index.csv"
    text = extract_context(text, model)
    if index.startswith("http://") or index.startswith("https://"):
        url = index
        index_filename= "datas/" + lib__embedded_context.build_index_url(url) + "/emb_index.csv"
    context = lib__embedded_context.find_context(text, index_filename, n_results=3)
    res = [{'id':1,'request':'searchcontext','answer':context}]
    response = jsonify(res)
    response.headers['Content-Type'] = 'application/json'
    return(response)

@app.route('/streamtasks', methods=['POST'])
@require_auth
def handle_stream_tasks():
    """
    Exécuter des tâches LLM en streaming (texte envoyé progressivement).
    - Entrée JSON: `script` (instructions), `model` (optionnel)
    - Flux: renvoie le texte au fur et à mesure de la génération
    """
    if not request.is_json:
        logger.warning("La requête doit contenir un JSON")
        return jsonify({"error": "La requête doit contenir un JSON"}), 400
    logger.info("Requête reçue : " + str(request.get_json()))
    model = request.get_json().get('model', DEFAULT_MODEL)
    logger.info("Modèle utilisé : " + str(model))
    model = DEFAULT_MODEL
    script = request.get_json().get('script')
    if script is None:
        logger.warning("Le JSON doit contenir un champ 'script'")
        return jsonify({"error": "Le JSON doit contenir un champ 'script'"}), 400
    try:
        json_file = "tmp/test" + str(random.randint(0, 1000)) + ".json"
        logger.info("script d'entrée :" + script)
        lib__script_tasks.text_to_json(script, json_file)
        tasks = lib__script_tasks.read_json_file(json_file)
        logger.info("Taches à executer " + str(tasks))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    try:
        return Response(lib__script_tasks.execute_tasks(tasks, model), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getvector', methods=['POST'])
@require_auth  # Ajouter cette ligne
def getvector():
    """
    Interroger un service Vectorize externe et récupérer des passages pertinents.
    - Entrée form: `question`, `vectordb`, `num_results`
    - Retour: contexte concaténé (JSON)
    """
    question = request.form.get('question')
    vectordb = request.form.get('vectordb')
    num_results = request.form.get('num_results', 5)
    retrieval_endpoint = "https://client.app.vectorize.io/api/gateways/service/" + vectordb + "/retrieve"
    context = lib_vectorize_context.retrieve_and_concatenate_texts(retrieval_endpoint, question, config.VECTORIZE_TOKEN, int(num_results))
    res = [{'id':1,'request':'searchcontext','answer':context}]
    response = jsonify(res)
    response.headers['Content-Type'] = 'application/json'
    return(response)

if __name__ == '__main__':
    app.run()
