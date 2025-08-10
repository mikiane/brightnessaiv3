# -*- coding: utf-8 -*-
"""
Script de veille automatique sur l'Intelligence Artificielle
Génère une newsletter quotidienne avec les dernières actualités IA
"""

from datetime import datetime
import locale
from libs import lib__config as config
from libs import lib__common_tasks as common
from libs import lib__agent_buildchronical

# Configuration des URLs à surveiller
URL_LIST = [
    "https://www.artificialintelligence-news.com/",
    "https://venturebeat.com/category/ai/",
    "https://www.wired.com/tag/artificial-intelligence/",
    "https://www.forbes.com/ai/",
    "https://www.theguardian.com/technology/artificialintelligenceai",
    "https://www.nature.com/natmachintell/",
    "https://towardsdatascience.com/",
    "https://openai.com/news/",
    "https://neurips.cc/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://techcrunch.com/tag/artificial-intelligence/"
]


def main():
    """Fonction principale du script de veille IA"""
    
    # Configuration de la locale (commenté car peut causer des problèmes sur certains systèmes)
    # locale.setlocale(locale.LC_TIME, 'fr_FR')
    
    # Date actuelle formatée
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d %B %Y")
    
    # Construction de la commande de veille
    command = common.build_watch_command(
        date=formatted_date,
        subject="l'IA",
        hours_ago=24,
        output_format="html",
        language="français"
    )
    
    # Traitement de toutes les URLs
    print(f"Démarrage de la veille IA pour le {formatted_date}")
    print(f"Traitement de {len(URL_LIST)} sources...")
    
    responses = common.process_multiple_urls(
        command=command,
        urls=URL_LIST,
        model=config.DEFAULT_MODEL,
        aggregate=True
    )
    
    # Nettoyage de la réponse HTML
    text_veille = common.clean_html_response(responses)
    
    # Envoi de la newsletter
    title = "AI WATCH : veille sur l'IA"
    email = "contact@brightness.fr"
    
    print(f"Envoi de la newsletter à {email}...")
    lib__agent_buildchronical.mail_html(title, text_veille, email)
    
    print("✅ Veille IA terminée avec succès")


if __name__ == "__main__":
    main()
