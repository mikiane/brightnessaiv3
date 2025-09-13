from openai import OpenAI
import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import html
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone


LOG_PATH = "/home/michel/docs/watch_crypto.log"

def setup_logging():
  logger = logging.getLogger("watch_crypto")
  if logger.handlers:
    return logger
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  try:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
  except Exception as e:
    logger.warning(f"Impossible de créer/ouvrir le fichier log {LOG_PATH}: {e}")
  return logger

log = setup_logging()
try:
  from dotenv import load_dotenv, find_dotenv
  load_dotenv(find_dotenv(), override=False)
except Exception:
  log.warning("python-dotenv non disponible; variables d'environnement uniquement.")

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
  log.info("Clé OPENAI_API_KEY détectée via env/.env")
else:
  log.warning("Aucune clé OPENAI_API_KEY détectée; tentative d'initialisation par défaut")
client = OpenAI(api_key=api_key) if api_key else OpenAI()

def extract_response_text(resp):
  try:
    parsed = getattr(resp, "output_parsed", None)
    if isinstance(parsed, (dict, list)):
      return json.dumps(parsed, ensure_ascii=False)
  except Exception:
    pass
  try:
    text = getattr(resp, "output_text", None)
    if isinstance(text, str) and text.strip():
      return text
  except Exception:
    pass
  try:
    output = getattr(resp, "output", None)
    if isinstance(output, list):
      parts = []
      for item in output:
        content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
        if isinstance(content, list):
          for c in content:
            t = c.get("text") if isinstance(c, dict) else getattr(c, "text", None)
            if isinstance(t, str) and t:
              parts.append(t)
      if parts:
        return "\n".join(parts)
  except Exception:
    pass
  try:
    text_attr = getattr(resp, "text", None)
    if isinstance(text_attr, str) and text_attr.strip():
      return text_attr
  except Exception:
    pass
  try:
    return str(resp)
  except Exception:
    return ""

def send_email_via_brevo(brevo_api_key, subject, text_body, to_email, sender_email, sender_name):
  if not brevo_api_key:
    log.error("BREVO_API_KEY manquant: envoi email ignoré.")
    return False
  url = "https://api.brevo.com/v3/smtp/email"
  html_body = f"<html><body><pre>{html.escape(text_body)}</pre></body></html>"
  payload = {
    "sender": {"name": sender_name, "email": sender_email},
    "to": [{"email": to_email}],
    "subject": subject,
    "textContent": text_body,
    "htmlContent": html_body
  }
  headers = {
    "api-key": brevo_api_key,
    "Content-Type": "application/json",
    "Accept": "application/json"
  }
  req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
  try:
    with urlopen(req) as resp:
      status = resp.getcode()
      if 200 <= status < 300:
        log.info("Email Brevo envoyé avec succès")
        return True
      log.error(f"Echec envoi email Brevo, status={status}")
      return False
  except HTTPError as e:
    try:
      body = e.read().decode("utf-8", errors="ignore")
    except Exception:
      body = ""
    log.exception(f"Erreur HTTP Brevo: {e.code} {body}")
    return False
  except URLError as e:
    log.error(f"Erreur réseau Brevo: {getattr(e, 'reason', e)}")
    return False
  except Exception as e:
    log.exception(f"Erreur inconnue Brevo: {e}")
    return False

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")


# Étape 1: Recherche web pour obtenir les données actuelles
log.info("Étape 1: Recherche des données crypto actuelles via web_search")
search_response = client.responses.create(
  model="gpt-5",
  store=False,
  tools=[{"type":"web_search"}],
  input=[
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": (
            f"Tu es un expert en crypto. Nous sommes le {today} (UTC). "
            "Recherche les prix actuels et actualités du jour pour BTC, ETH, SOL "
            "et les principales altcoins. Trouve les niveaux de support/résistance, "
            "les tendances du marché et les événements macro importants."
          )
        }
      ]
    }
  ],
  text={
    "verbosity": "medium"
  },
  reasoning={
    "effort": "high",
    "summary": "auto"
  },
)

# Extraire les données de la recherche
search_data = extract_response_text(search_response)
log.info("Données crypto récupérées via web_search")

# Étape 2: Génération du JSON structuré avec les données récupérées
log.info("Étape 2: Génération du rapport JSON structuré")
response = client.responses.create(
  model="gpt-5",
  store=False,
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": (
            f"Tu es un expert crypto. Voici les données actuelles du marché:\n\n{search_data}\n\n"
            f"Date: {today} (UTC). Génère un rapport structuré en JSON strict."
          )
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": """Developer:
Objectif: produire un brief crypto swing/HODL (max 2 A/R par mois), en français.
Contraintes:
- Utilise les données fournies pour créer le rapport.
- Réponds UNIQUEMENT en JSON strict conforme au schéma imposé par l'API; aucune prose hors JSON; aucune source/URL.
- Remplis toutes les sections requises avec des valeurs cohérentes (USD, %, ratios R/R float, TP/SL/entry précis, supports/résistances numériques).
Focus: ETH, BTC, SOL; 0–2 altcoins pertinents; plan hebdomadaire synthétique; risques macro/agenda clés.
"""
        }
      ]
    }
  ],
  
  text={
    "format": {
      "type": "json_object"
    },
    "verbosity": "medium"
  },
  reasoning={
    "effort": "high",
    "summary": "auto"
  },
)
log.info("Réponse générée par le modèle gpt-5")

generated_text = extract_response_text(response)
if generated_text:
  log.info(f"Texte généré: {min(len(generated_text), 200)} caractères (tronqué dans les logs)")
else:
  log.warning("Aucun texte généré extrait de la réponse")

brevo_api_key = os.getenv("BREVO_API_KEY")
sender_email = os.getenv("BREVO_SENDER_EMAIL", "no-reply@brightness.fr")
sender_name = os.getenv("BREVO_SENDER_NAME", "Brightness AI")
to_email = "michel@brightness.fr"
subject = "Veille Crypto"

_email_ok = send_email_via_brevo(
  brevo_api_key=brevo_api_key,
  subject=subject,
  text_body=generated_text,
  to_email=to_email,
  sender_email=sender_email,
  sender_name=sender_name,
)
log.info(f"Envoi email Brevo: {'OK' if _email_ok else 'ECHEC'}")

# Ecriture du fichier JSON généré dans ../front/crypto-agent/latest.json
try:
  out_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "front", "crypto-agent"))
  os.makedirs(out_dir, exist_ok=True)
  out_path = os.path.join(out_dir, "latest.json")
  if generated_text:
    try:
      data = json.loads(generated_text)
      with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
      log.info(f"Fichier JSON écrit: {out_path}")
    except Exception:
      with open(out_path, "w", encoding="utf-8") as f:
        f.write(generated_text)
      log.info(f"Texte écrit (non parsé) vers: {out_path}")
  else:
    log.warning("Aucun texte généré; fichier latest.json non écrit.")
except Exception as e:
  log.exception(f"Erreur écriture latest.json: {e}")