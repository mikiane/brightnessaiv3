# -*- coding: utf-8 -*-
"""
Fonctions communes pour la veille
- `process_url` et `process_rss`: extraient le contenu et appellent le LLM
- `process_multiple_urls`: gère plusieurs sources et agrège
- `build_watch_command`: fabrique un prompt standardisé (explications claires)
"""

from libs import lib__agent_buildchronical
from typing import Optional
from libs import lib__config as config
logger = config.logger


def process_url(
    command: str,
    url: str,
    model: str = None,
    site: str = "",
    input_data: str = ""
) -> str:
    """
    Traite une URL et génère une réponse basée sur la commande et le contenu de l'URL
    
    Args:
        command: La commande/prompt à exécuter
        url: L'URL à traiter
        model: Le modèle LLM à utiliser (optionnel)
        site: Information sur le site (optionnel)
        input_data: Données d'entrée supplémentaires (optionnel)
    
    Returns:
        La réponse générée par le modèle
    """
    # Récupération du contenu
    content = lib__agent_buildchronical.fetch_and_parse_urls(url)
    content = content.replace('\n', '')
    
    # Construction du prompt
    prompt = f"{command}\n ___ {content}\n ___ \n"
    logger.debug(f"Prompt URL construit (début): {prompt[:300]}...")
    
    # Exécution avec le modèle
    res = lib__agent_buildchronical.execute(prompt, site, input_data, model)
    logger.info(f"URL traitée: {url}")
    return res


def process_rss(
    command: str,
    rss_url: str,
    model: str = None,
    site: str = "",
    input_data: str = ""
) -> str:
    """
    Traite un flux RSS et génère une réponse basée sur la commande
    
    Args:
        command: La commande/prompt à exécuter
        rss_url: L'URL du flux RSS
        model: Le modèle LLM à utiliser (optionnel)
        site: Information sur le site (optionnel)
        input_data: Données d'entrée supplémentaires (optionnel)
    
    Returns:
        La réponse générée par le modèle
    """
    # Récupération du contenu RSS via lib__agent_buildchronical
    content = lib__agent_buildchronical.fetch_and_parse_rss_to_string(rss_url)
    content = content.replace('\n', '')
    
    # Construction du prompt
    prompt = f"{command}\n ___ {content}\n ___ \n"
    logger.debug(f"Prompt RSS construit (début): {prompt[:300]}...")
    
    # Exécution avec le modèle
    res = lib__agent_buildchronical.execute(prompt, site, input_data, model)
    logger.info(f"RSS traité: {rss_url}")
    return res


def process_multiple_urls(
    command: str,
    urls: list,
    model: str = None,
    aggregate: bool = True
) -> str:
    """
    Traite plusieurs URLs et agrège les résultats
    
    Args:
        command: La commande/prompt à exécuter
        urls: Liste des URLs à traiter
        model: Le modèle LLM à utiliser
        aggregate: Si True, combine tous les résultats en une seule réponse
    
    Returns:
        Les réponses générées (combinées ou séparées)
    """
    responses = []
    
    for url in urls:
        try:
            if "rss" in url or "feed" in url or url.endswith(".xml"):
                res = process_rss(command, url, model)
            else:
                res = process_url(command, url, model)
            responses.append(res)
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {url}: {e}")
            continue
    
    if aggregate:
        return "<br><br>".join(responses)
    else:
        return responses


def clean_html_response(response: str) -> str:
    """
    Nettoie une réponse HTML en supprimant les balises markdown
    
    Args:
        response: La réponse brute potentiellement avec des balises markdown
    
    Returns:
        La réponse nettoyée
    """
    # Supprime les balises ```html et ```
    cleaned = response.replace("```html", "").replace("```", "")
    
    # Supprime les espaces en début et fin
    cleaned = cleaned.strip()
    
    return cleaned


def build_watch_command(
    date: str,
    subject: str,
    hours_ago: int = 24,
    output_format: str = "html",
    language: str = "français"
) -> str:
    """
    Construit une commande standard pour les scripts de veille
    
    Args:
        date: La date formatée
        subject: Le sujet de la veille (ex: "l'IA", "les tendances tech")
        hours_ago: Nombre d'heures pour filtrer les articles récents
        output_format: Format de sortie souhaité (html, markdown, text)
        language: Langue de sortie
    
    Returns:
        La commande formatée
    """
    
    if output_format == "html":
        format_instructions = """
        Toujours utiliser un modele de page HTML fond blanc, avec :
        - Titre en rouge en <h3>
        - Description en <p> noir
        - Tweet en <p> sur fond bleu clair
        - Lien vers l'article derriere un 'Read More'
        """
    elif output_format == "markdown":
        format_instructions = """
        Formater en Markdown avec :
        - Titre en ## 
        - Description en paragraphe normal
        - Tweet en blockquote (>)
        - Lien en format [Read More](url)
        """
    else:
        format_instructions = "Formater en texte simple avec des séparations claires."
    
    command = f"""Nous sommes le {date}
    À partir du texte suivant entre ___ , contenant des listes et descriptions des derniers articles sur {subject}.
    Extraire TOUS les articles datant d'il y a moins de {hours_ago} heures et générer la liste exhaustive des informations récentes mentionnées dans le texte.
    Aucun article datant de moins de {hours_ago} heures ne doit être oublié.
    
    La liste doit comprendre les informations suivantes :
    - Titre de l'article (traduit en {language})
    - Description / résumé de l'article (traduit en {language})
    - Pour chaque article ajouter l'url associée. 
    
    Répondre directement en générant la liste. Ne converse pas. Ne conclue pas.
    Ne pas générer d'introduction ni de conclusion, juste la liste.
    {format_instructions}
    Démarrer la liste avec le titre de la source.
    """
    
    return command.strip() 