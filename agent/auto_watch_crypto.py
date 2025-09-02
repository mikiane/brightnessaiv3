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


response = client.responses.create(
  model="gpt-5",
  # clé pour démarrer "à blanc" chaque jour
  store=False,  # <<< important
  tools=[{"type":"web_search"}],
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": (
            f"Tu es un expert en crypto. Nous sommes le {today} (UTC). Ignore tout contexte antérieur. "
            "Tu DOIS utiliser web_search pour récupérer les PRIX/ACTUS du jour "
            "et tu cites la date des données."
          )
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Developer: # Rôle et Objectif\nCréer un rapport synthétique, actionnable et strictement structuré pour une stratégie HODL/swing crypto avec un maximum de 2 allers-retours par mois, uniquement sur les opportunités les plus pertinentes.\n\n# Instructions\n- Générer un rapport en français clair et pédagogique, sous forme de texte facilement lisible (pas de JSON).\n- Structurer impérativement le contenu par les sections suivantes :\n  1. Ethereum (ETH)\n  2. Bitcoin (BTC)\n  3. Solana (SOL)\n  4. Autres altcoins (1 ou 2, selon actualité)\n  5. Plan hebdomadaire synthétique\n  6. Risque macro/marché\n- Adapter la structure détaillée pour chaque crypto selon les besoins ci-dessous, en restant dans un format texte structuré par rubrique.\n- Toutes les valeurs numériques doivent apparaître dans le rapport en respectant les formats requis : prix en USD, pourcentages, ratios gain/risque (float), etc.\n- Les ordres doivent être formulés comme s’ils devaient être placés directement sur un exchange, avec des niveaux de prix précis.\n\n## Sous-catégories\n- ETH/BTC/SOL :\n  - Inclure tendance macro, niveaux clés supports/résistances, signaux d’entrée détaillés (type, prix, confirmation), TP, SL (avec buffer), justification (technique et fondamentale), risque et potentiel (%), ratio R/R (float), effet de levier conseillé.\n- Altcoins :\n  - Maximum 2, selon l’actualité. Présenter chaque actif par symbole et inclure breakout/TP/SL/justification/ratio dans un paragraphe clair.\n- Plan hebdo :\n  - Synthétiser une liste concise et priorisée d’actions avec conditions de niveau prix, maximum 2 A/R par mois.\n- Macro risque :\n  - Lister les événements majeurs et indiquer toute alerte de volatilité/manipulation dans un encadré.\n\n# Contexte\n- Applicable pour une stratégie swing/HODL en crypto, principalement spot mais effet de levier jusqu’à x2 possible.\n- En-dehors du scope : scalping/intraday, plus de 2 allers-retours par mois, signaux peu pertinents ou monnaies non listées.\n\n# Étapes de raisonnement\n- Analyser les tendances et actualités majeures.\n- Sélectionner uniquement les signaux très pertinents pour chaque actif.\n- Détaillez et justifiez chaque proposition d’ordre selon les critères définis, en format texte.\n\n# Planification et vérification\n- Vérifier la cohérence des niveaux de prix, ratios, justificatifs et la structure finale du texte.\n- S’assurer qu’aucune section ne soit manquante ou vide.\n- Limiter le nombre total d’allers-retours à 2 par mois sur l’ensemble du rapport.\n- Optimiser la clarté et la concision à chaque étape.\n- Débuter par une checklist concise (3-7 points conceptuels) des tâches à réaliser avant tout traitement substantiel.\n- Après génération, conclure par 1-2 phrases validant le respect de tous les critères de structure, format et limites. Corriger et régénérer si besoin.\n\n# Format de sortie\n- Générer la réponse sous forme de texte structuré, chaque section clairement identifiée et toutes les valeurs chiffrées explicitement indiquées.\n- Chaque altcoin est décrit individuellement dans la section correspondante.\n- Le \"plan hebdomadaire\" ne doit jamais proposer plus de 2 A/R par mois.\n- La section \"risque macro\" mentionne à la fois les événements importants et les risques de manipulation ou de volatilité dans un paragraphe dédié.\n\n# Contrôle de format strict\n- Toutes les informations exigées par le schéma doivent être présentes et correctement formatées dans le texte, aucune section ne doit manquer."
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "text"
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