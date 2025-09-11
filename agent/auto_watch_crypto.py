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
          "text": "🎯 Contrat de la journée Clarifier et sécuriser les partenariats prioritaires (Nespresso, TEDFOOD), finaliser le code TEDAI Vienna (overdue), et assurer les rendez-vous médias & partenaires (BFM, déjeuner, Ruis) pour maintenir l’élan des projets semestriels. 📌 Projets & Actions 🌐 TED / TEDx / Conférences Code d’accès TEDAI Vienna (P1, overdue) Action : confirmer le code (801764) dans le doc public + transmettre aux participants. (~15 min) Appel TEDx Technion (11:30–12:00) Action : relire les 3 points clés (format & calendrier) et préparer téléphone. Email Nespresso (TEDxParis 2026) Répondre à Nathalie Gonzalez avant midi : Bonjour Nathalie, merci pour ta franchise et le retour. Je comprends la priorisation 2026. Peut-on prévoir un court échange (15-20 min) cette semaine pour explorer une option de visibilité limitée / partenariat technique qui s'intègre à vos priorités actuelles ? Quels créneaux te conviennent ? — Michel Email Andrea Grundelius (TEDFOOD 2027) Réponse courte à envoyer : Merci Andrea — bien noté, je confirme l'enregistrement des dates de la semaine 36 (6–10 sept 2027). Email Maylis (Brightness — minutes du 9 sept) Vérifier et confirmer (ou corriger). Réponse : Merci Maylis — j'ai lu les minutes, elles me semblent correctes / je propose une petite correction sur [X] si nécessaire. 💼 Brightness / Partenariats & Business Déjeuner Vincent Susplugas (12:30–14:00) Lieu : Garçon ! — apporter docs / préparer points commerciaux. RDV Ruis (15:00–16:45) Préparer brief et documents pertinents. 🎙️ Médias & Interventions Prépa BFM (17:30–19:30) Finaliser messages clés, slides, notes. Intervention BFM (19:30–20:45) Tenue, micro, dernières notes. 🧑‍💻 Organisation & Développement perso Formation GTD + IA (P2) Avancer sur module, planifier plan d’action. (60 min, créneau 14:00–15:00). 🛠️ Perso & Logistique Récupérer sac Leica Beaumarchais (P1) (~30 min, avant 10:30). Arrosage plantes (P3) (15 min, 09:45–10:00 ou 21:00–21:15). Email Caroline (scooter) : suivre ou archiver. Email Julie Martinez (France 2040) : lecture non urgente, déplacer en hebdo. Vérifier : téléphone chargé, powerbank, copies PDF TEDx/TEDFOOD sur smartphone. Préparer tenue pro pour BFM."
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