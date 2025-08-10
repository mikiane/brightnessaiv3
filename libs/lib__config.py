# -*- coding: utf-8 -*-
"""
Configuration centralisée de l’application
- Charge le fichier .env une seule fois et expose les variables au reste du code
- Fournit un logger unique (`config.logger`) utilisé partout
- Clés importantes: OPENAI_API_KEY, DEFAULT_MODEL, chemins (PODCASTS_PATH, LOCALPATH), tokens (SENDGRID_KEY, ELEVENLABS_API_KEY, etc.)
"""

import os
import logging
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Prépare le logger tôt pour logguer le chemin .env
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_probe_logger = logging.getLogger("libs.lib__config")

# Charger le .env (recherche à partir du cwd en remontant), fallback sur libs/.env
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)
    _probe_logger.info(f".env chargé depuis: {dotenv_path}")
else:
    ENV_PATH = Path(__file__).parent / '.env'
    load_dotenv(ENV_PATH)
    _probe_logger.info(f".env (fallback) chargé depuis: {ENV_PATH}")

# Configuration des chemins
BASE_PATH = Path(__file__).parent
DATAS_PATH = BASE_PATH / "datas"
TMP_PATH = BASE_PATH / "tmp"
PODCASTS_PATH = os.environ.get("PODCASTS_PATH", str(BASE_PATH / "podcasts"))
LOCALPATH = os.environ.get("LOCALPATH", str(BASE_PATH))

# Clés API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_AI_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
SENDGRID_KEY = os.environ.get("SENDGRID_KEY")
XAI_KEY = os.environ.get("XAI_KEY")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")

# Clé de sécurité pour les appels frontend
FRONT_BRIGHTNESS_KEY = os.environ.get("FRONT_BRIGHTNESS_KEY")
VECTORIZE_TOKEN = os.environ.get("VECTORIZE_TOKEN")
# Ajouts Phase 4
ACAST_API_KEY = os.environ.get("ACAST_API_KEY")
FEEDLY_API_TOKEN = os.environ.get("FEEDLY_API_TOKEN")
GOOGLE_API_TOKEN = os.environ.get("GOOGLE_API_TOKEN")
CSE_ID = os.environ.get("CSE_ID")
DESTINATAIRES_TECH = os.environ.get("DESTINATAIRES_TECH")

# AWS Configuration
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
REGION_NAME = os.environ.get("REGION_NAME", "eu-west-1")

# Modèles par défaut
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4")
DEFAULT_EMBEDDING_MODEL = os.environ.get("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
MODEL_URL = os.environ.get("MODEL_URL", "")

# Configuration de l'application
APP_PATH = os.environ.get("APP_PATH", str(BASE_PATH))
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# Configuration Langchain
LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", "true")

# Configuration du logging
def setup_logging(level=logging.INFO):
    """Configure le système de logging pour toute l'application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BASE_PATH / 'app.log')
        ]
    )
    return logging.getLogger(__name__)

# Logger par défaut
logger = setup_logging()

# Validation des clés critiques
def validate_config():
    """Valide que les clés API critiques sont présentes"""
    critical_keys = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "DEFAULT_MODEL": DEFAULT_MODEL
    }
    
    missing_keys = [key for key, value in critical_keys.items() if not value]
    
    if missing_keys:
        logger.warning(f"⚠️  Variables d'environnement manquantes : {', '.join(missing_keys)}")
        logger.warning("Veuillez vérifier votre fichier .env")
    
    return len(missing_keys) == 0

# Validation au chargement du module
if __name__ != "__main__":
    validate_config() 