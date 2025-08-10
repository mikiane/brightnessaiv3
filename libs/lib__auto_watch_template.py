# -*- coding: utf-8 -*-
"""
Template unifié pour scripts de veille (auto_watch_*_v2)
- Idée: factoriser la logique commune (construction du prompt, traitement URLs/RSS, email)
- Utilisation: chaque `auto_watch_*_v2.py` instancie un bot via une fonction factory (ex: create_ted_watch)
"""

from datetime import datetime
import locale
from libs import lib__config as config
from libs import lib__common_tasks as common
from libs import lib__agent_buildchronical
import logging
logger = config.logger

class AutoWatchBot:
    """Bot générique de veille: configure des sources (urls/rss) et exécute la veille.
    - Attributs principaux: name, subject, email, urls, rss_feeds
    - Méthode `run`: construit un prompt standard, traite les sources et (optionnel) envoie l’email
    """
    def __init__(self, name: str, subject: str, email: str = "contact@brightness.fr", custom_command: str = None):
        self.name = name
        self.subject = subject
        self.email = email
        self.urls = []
        self.rss_feeds = []
        self.custom_command = custom_command
    def add_urls(self, urls: list):
        """Ajouter une liste d’URLs web à surveiller."""
        self.urls.extend(urls)
    def add_rss_feeds(self, feeds: list):
        """Ajouter une liste de flux RSS à surveiller."""
        self.rss_feeds.extend(feeds)
    def run(self, hours_ago: int = 24, model: str = None, send_email: bool = True):
        """Exécuter la veille: construit le prompt, traite les sources, et envoie (ou renvoie) le résultat."""
        try:
            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_TIME, 'fr_FR')
                except:
                    logger.warning("Impossible de configurer la locale française")
            current_date = datetime.now()
            formatted_date = current_date.strftime("%d %B %Y")
            logger.info(f"Démarrage de {self.name} pour le {formatted_date}")
            logger.info(f"Sources: {len(self.urls)} URLs, {len(self.rss_feeds)} RSS")
            command = self.custom_command or common.build_watch_command(
                date=formatted_date, subject=self.subject, hours_ago=hours_ago, output_format="html", language="français"
            )
            all_sources = self.urls + self.rss_feeds
            if not all_sources:
                logger.error("Aucune source configurée pour la veille")
                return
            responses = common.process_multiple_urls(
                command=command, urls=all_sources, model=model or config.DEFAULT_MODEL, aggregate=True
            )
            text_veille = common.clean_html_response(responses)
            if send_email:
                logger.info(f"Envoi de la newsletter à {self.email}...")
                lib__agent_buildchronical.mail_html(self.name, text_veille, self.email)
                logger.info(f"{self.name} terminée avec succès")
            else:
                logger.info(f"{self.name} générée (email non envoyé)")
                return text_veille
        except Exception as e:
            logger.error(f"Erreur dans {self.name}: {str(e)}", exc_info=True)
            raise

# Les factories suivantes préconfigurent un bot pour un thème donné (sources intégrées)
# Ex: `create_ted_watch()` crée un bot qui surveille le flux RSS TED


def create_ai_watch():
    """Factory pour créer le bot de veille IA"""
    bot = AutoWatchBot("AI WATCH : veille sur l'IA", "l'IA")
    bot.add_urls([
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
    ])
    return bot


def create_ted_watch():
    """Factory pour créer le bot de veille TED"""
    bot = AutoWatchBot("TED WATCH : veille sur TED.com", "les dernières vidéos sur TED.com")
    bot.add_rss_feeds([
        "https://pa.tedcdn.com/feeds/talks.rss"
    ])
    return bot


def create_publicspeaking_watch():
    """Factory pour créer le bot de veille Public Speaking"""
    bot = AutoWatchBot("Public Speaking WATCH : veille sur Public Speaking", "le thème du Public Speaking")
    bot.add_rss_feeds([
        "https://rss.app/feeds/tZTJRd8QbKQoXf6q.xml"
    ])
    return bot


def create_ld_watch():
    """Factory pour créer le bot de veille Learning & Development"""
    bot = AutoWatchBot("L&D WATCH : veille sur Learning & Development", "le thème du Learning & Development")
    bot.add_rss_feeds([
        "https://rss.app/feeds/tevRvhjRb3jyhRmQ.xml"
    ])
    return bot


def create_debatsetidees_watch():
    """Factory pour créer le bot de veille Débats et Idées"""
    bot = AutoWatchBot("Ideas & Debats WATCH : veille idées et débats", "les rubriques débats et idées", email="contact@brightness.fr")
    bot.add_rss_feeds([
        "https://rss.app/feeds/_iyxJsrcv3zlT7f9x.xml"
    ])
    return bot


def create_allinno_watch():
    """Factory pour créer le bot de veille Tech/Innovation"""
    bot = AutoWatchBot("Techno WATCH : veille sur Techno", "les actus technologiques")
    bot.add_urls([
        'https://techcrunch.com',
        'https://www.wired.com',
        'https://arstechnica.com',
        'https://www.theverge.com',
        'https://mashable.com',
        'https://www.cnet.com',
        'https://www.engadget.com',
        'https://gizmodo.com',
        'https://www.technologyreview.com',
        'https://venturebeat.com',
        "https://www.bbc.com/news/technology",
        "https://www.theguardian.com/uk/technology",
        "https://www.telegraph.co.uk/technology/",
        "https://www.reuters.com/technology/",
        "https://www.bloomberg.com/technology",
        "https://www.ft.com/technology",
        "https://www.haaretz.com/israel-news/tech-news",
        "https://www.calcalistech.com/",
        "https://www.globes.co.il/en/",
        "https://www.lemonde.fr/technologies/",
        "https://www.numerama.com/tech/",
        "https://www.euronews.com/programmes/actualite-tech",
        "https://www.lemondeinformatique.fr/"
    ])
    return bot


def create_trendspotting_watch():
    """Factory pour créer le bot de veille Livres/Trendspotting"""
    custom_command = """A partir du texte suivant entre ___ , contenant des listes et descriptions de livres, extraire et générer la liste exhaustive des livres mentionnés dans le texte.
        La liste doit comprendre les informations suivantes : 
            Titre de l'ouvrage 
            <br>Auteur de l'ouvrage 
            <br>Éditeur 
            <br>URL associée au livre. 
            Ne pas générer d'introduction ni de conclusion, juste la liste. 
            Toujours utiliser un modele de page HTML fond blanc, avec Titre en rouge en <h3>, description en <p> noir sur fond bleu clair, lien vers le livre derriere un Read More.
            Démarrer la liste avec le titre de la source."""
    
    bot = AutoWatchBot(
        "TRENDSPOTTING : veille livres à paraître", 
        "livres", 
        email="michel@brightness.fr",
        custom_command=custom_command
    )
    bot.add_urls([
        "https://www.hachette.fr/a-paraitre/histoire-et-actualite",
        "https://www.grasset.fr/a-paraitre/",
        "https://www.diateino.com/nouveautes.php",
        "https://www.belin-editeur.com/sciences-belin",
        "https://editions.flammarion.com/Catalogue/(parution)/a-paraitre/(domaine)/Sciences humaines",
        "https://editions.flammarion.com/Catalogue/(parution)/a-paraitre/(domaine)/Essais et documents",
        "https://www.actes-sud.fr/recherche/catalogue/rayon/1198?keys=",
        "https://www.albin-michel.fr/essais-docs",
        "https://www.albin-michel.fr/sciences-humaines",
        "https://www.seuil.com/a-paraitre",
        "https://www.dunod.com/recherche/etat/Nouveaut%C3%A9",
        "https://www.puf.com/search?search_api_fulltext=&f%5B0%5D=discipline%3A593",
        "https://www.puf.com/search?search_api_fulltext=&f%5B0%5D=discipline%3A561",
        "https://www.puf.com/search?search_api_fulltext=&f%5B0%5D=discipline%3A541",
        "https://www.odilejacob.fr/catalogue/",
        "https://www.fayard.fr/a-paraitre/",
        "http://editions.ehess.fr/a-paraitre/"
    ])
    return bot


def create_innovation_watch():
    """Factory pour créer le bot de veille Innovation"""
    bot = AutoWatchBot("INNOVATION WATCH", "l'innovation")
    bot.add_urls([
        "https://www.wired.com/",
        "https://techcrunch.com/",
        "https://www.technologyreview.com/",
        "https://www.fastcompany.com/technology"
    ])
    return bot 