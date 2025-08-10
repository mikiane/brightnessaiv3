# ----------------------------------------------------------------------------
# Recherche de sources (Feedly, Google CSE)
# - `get_feedly_feeds(topic, n)`: renvoie des paires [titre, feedId]
# - `google_search(...)`: interroge l’API Custom Search
# ----------------------------------------------------------------------------

import requests
from googlesearch import search
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from libs import lib__config as config
logger = config.logger
FEEDLY_API_TOKEN = config.FEEDLY_API_TOKEN
GOOGLE_API_TOKEN = config.GOOGLE_API_TOKEN
CSE_ID = config.CSE_ID


def get_feedly_feeds(topic, n):
    url = f"https://feedly.com/v3/search/feeds?query={topic}&count={n}"
    headers = {
        'Authorization': f'OAuth {FEEDLY_API_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f'Error with status code: {response.status_code}')
        return []
    data = response.json()
    results = []
    for item in data.get('results', []):
        title = item.get('title')
        feed_id = item.get('feedId')
        results.append([title, feed_id])
    if not results:
        logger.info("Aucun résultat trouvé")
    return results


def google_search(search_term, api_key=GOOGLE_API_TOKEN, cse_id=CSE_ID, num_results=5):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, num=num_results).execute()
    if 'items' in res:
        return res['items']
    else:
        logger.info("Aucun résultat trouvé")
        return []

