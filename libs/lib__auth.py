# -*- coding: utf-8 -*-
"""
Module de sécurisation des API Flask
Autorise les requêtes depuis *.brightness.agency ou avec une clé API valide
"""

from functools import wraps
from flask import request, jsonify, abort
from urllib.parse import urlparse
import re
from libs import lib__config as config

# Récupérer la clé secrète depuis la config
FRONT_BRIGHTNESS_KEY = config.FRONT_BRIGHTNESS_KEY if hasattr(config, 'FRONT_BRIGHTNESS_KEY') else None
logger = config.logger

# Domaines autorisés (regex pour matcher *.brightness.agency ET *.brightness-agency.com)
ALLOWED_DOMAINS_PATTERN = re.compile(r'^(https?://)?([\w\-]+\.)?(brightness\.agency|brightness\-agency\.com)')

def check_auth():
    """
    Vérifie l'autorisation de la requête
    Retourne True si autorisée, False sinon
    """
    # 1. Vérifier l'origine (Origin header)
    origin = request.headers.get('Origin', '')
    if origin and ALLOWED_DOMAINS_PATTERN.match(origin):
        logger.debug(f"Authorized request from allowed domain: {origin}")
        return True
    
    # 2. Vérifier le Referer comme fallback
    referer = request.headers.get('Referer', '')
    if referer and ALLOWED_DOMAINS_PATTERN.match(referer):
        logger.debug(f"Authorized request from allowed referer: {referer}")
        return True
    
    # 3. Vérifier la clé API dans les headers
    api_key = request.headers.get('X-API-Key', '')
    if not api_key:
        # Essayer aussi dans Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
    
    if api_key and FRONT_BRIGHTNESS_KEY and api_key == FRONT_BRIGHTNESS_KEY:
        logger.debug("Authorized request with valid API key")
        return True
    
    # 4. Vérifier la clé API dans les paramètres de requête (moins sécurisé mais pratique)
    if request.method == 'GET':
        api_key = request.args.get('api_key', '')
    else:
        # Pour POST, vérifier dans le JSON body
        try:
            data = request.get_json(silent=True) or {}
            api_key = data.get('api_key', '')
        except:
            api_key = ''
    
    if api_key and FRONT_BRIGHTNESS_KEY and api_key == FRONT_BRIGHTNESS_KEY:
        logger.debug("Authorized request with valid API key in params")
        return True
    
    # Non autorisé
    logger.warning(f"Unauthorized request from {origin or referer or 'unknown'}")
    return False


def require_auth(f):
    """
    Décorateur pour protéger une route Flask
    Usage:
        @app.route('/api/endpoint')
        @require_auth
        def my_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_auth():
            # Retourner une erreur 403 Forbidden
            abort(403, description="Access denied. Request must come from authorized domain or include valid API key.")
        return f(*args, **kwargs)
    return decorated_function


def setup_cors(app):
    """
    Configure CORS pour l'application Flask
    Permet les requêtes depuis brightness.agency, brightness-agency.com et localhost (dev)
    """
    from flask_cors import CORS
    
    # Configuration CORS pour les domaines autorisés
    cors_config = {
        "origins": [
            # brightness.agency (prod)
            "https://*.brightness.agency",
            "http://*.brightness.agency",
            # brightness-agency.com (prod et env dev)
            "https://*.brightness-agency.com",
            "http://*.brightness-agency.com",
            # sous-domaine spécifique explicitement (au cas où le wildcard ne serait pas supporté côté proxy)
            "https://dev.brightness-agency.com",
            "http://dev.brightness-agency.com",
            # localhost (dev)
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
        "supports_credentials": True
    }
    
    CORS(app, resources={r"/*": cors_config})
    logger.info("CORS configured for brightness.agency and brightness-agency.com domains")


def add_security_headers(response):
    """
    Ajoute des headers de sécurité à la réponse
    À utiliser avec app.after_request
    """
    # Headers de sécurité basiques
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Limiter les referrers
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response


# Middleware pour logger toutes les requêtes (optionnel)
def log_request():
    """Log les détails de la requête pour debug"""
    logger.info(f"Request: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Origin: {request.headers.get('Origin', 'None')}")
    logger.debug(f"Referer: {request.headers.get('Referer', 'None')}")
