import requests
import json
from libs import lib__config as config

# Extrait le text de JSON

def extract_and_concatenate_texts(json_input):
    try:
        data = json.loads(json_input)
        value = json.loads(data['record']['value'])
        if 'related_documents' in value and value['related_documents']:
            texts = [doc['text'] for doc in value['related_documents']]
            concatenated_texts = "\n\n".join(texts)
        else:
            concatenated_texts = "Aucun contxte trouvé."
    except json.JSONDecodeError:
        concatenated_texts = "Erreur dans le format."
    except KeyError:
        concatenated_texts = "Données manquantes."
    return concatenated_texts

# Appelle Vectorize

def retrieve_and_concatenate_texts(endpoint, question, token, num_results=5):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token or config.VECTORIZE_TOKEN
    }
    data = {
        "question": question,
        "numResults": num_results,
        "rerank": True
    }
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.text
        return extract_and_concatenate_texts(json_response)
    except requests.exceptions.RequestException as e:
        return f"Erreur de requête: {e}"
    except Exception as e:
        return f"Erreur inattendue: {e}"

# Exemple d'utilisation (commenté)
# question = "Parle moi de scenario planning"
# retrieval_endpoint = "https://client.app.vectorize.io/api/gateways/service/o38d-e267e6a43523/peb269e55/retrieve"
# result = retrieve_and_concatenate_texts(retrieval_endpoint, question, config.VECTORIZE_TOKEN)
# print(result)