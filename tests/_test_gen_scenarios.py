import lib_genpodcasts
import lib__agent_buildchronical
import random
import datetime
from datetime import date
from datetime import datetime
import locale
import lib__transformers
import json
import lib__embedded_context
import os
import requests
import time
import openai
from urllib.parse import unquote
from queue import Queue
from datetime import *
from lib__env import *
from openai import OpenAI
import sys
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import json
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests





load_dotenv(".env")
DESTINATAIRES_TECH = os.environ.get("DESTINATAIRES_TECH")
PODCASTS_PATH = os.environ.get("PODCASTS_PATH")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL")
ACAST_API_KEY = os.environ.get("ACAST_API_KEY")
model = DEFAULT_MODEL


secteur = "Techonologies de l'information"
horizon = "2035"
precisions = "ATTENTION : Prendre en compte les aspects géopolitiques est fondamental pour ce secteur. La question de la souveraineté (ou non) également. "

## TENDANCES ##

def generate_result (prompt, model="gpt-4o"):
    if (model == "perplexity"):
        model="llama-3.1-sonar-huge-128k-online"
        temperature=0.01
        max_retries=4
        url = "https://api.perplexity.ai/chat/completions"
        api_key = os.getenv("PPLX_API_KEY")  # Assurez-vous que la clé API est définie dans l'environnement

        if not api_key:
            raise ValueError("La clé API Perplexity (PPLX_API_KEY) n'est pas définie dans les variables d'environnement.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_message = "Je suis un assistant parlant parfaitement le français et l'anglais."

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,  # Ajustez selon vos besoins
            "temperature": temperature,
            "return_images": False,
            "return_related_questions": False,
            "stream": False,
        }

        attempts = 0

        while attempts < max_retries:
            try:
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    # Extraire le contenu du message généré par l'assistant
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    print(f"Erreur HTTP {response.status_code}: {response.text}")

            except Exception as e:
                error_code = type(e).__name__
                error_reason = str(e)
                attempts += 1
                print(f"Erreur : {error_code} - {error_reason}. Nouvel essai dans {attempts * 5} secondes...")
                time.sleep(attempts * 5)

        print("Erreur : Échec de la génération de la réponse après 10 essais.")
        return None

    else:
        res=lib_genpodcasts.call_llm(prompt, "", "", model, 14000)
    return(str(res))

prompt1 = f"Je voudrais que tu identifier 5 tendances majeures et disruptives (S: Sociale, T: Technologique, E: Economique, E: Environnemental, P: Politique) \
    succebtibles d'impacter de manière significative les entreprises française du secteur suivant : {secteur} à l'horizon temporel {horizon}. Les tendances doivent etre \
    les plus impactantes et plausibles. Il faut etre précis sur les tendances et surtout donner \
    quelques exemples de signaux qui motivent le choix de ces tendances. \n\n{precisions}\n\n"



res3 = generate_result(prompt1, "perplexity")



prompt4 = f"Voici les tendances sur lesquelles tu vas te baser à présent : <tendances>{res3}</tendances>\
    Peux tu intégrer dans la liste suivante des éléments concrets, des exemples, des projets, des actualités qui sous-tendent chacune de ces tendances. \n\n{precisions}"
res4 = generate_result(prompt4, "perplexity")



prompt5 = f"Peux tu  dégager de cette liste les 4 tendances qui te semblent les plus disruptives et mais les plus plausibles à l’horizon {horizon} pour le secteur de {secteur} <listes>\n\n{res4}\n\n</listes>\n\n{precisions}"
res5 = generate_result(prompt5, "perplexity")


print("#### Voici les tendances identifiées : \n\n" + res3 + "\n\n" + res4 + "\n\n" + res5 + "\n\n\n\n")

### SCENARIOS ###

prompt6 = f"A partir des tendances prioritaires selectionnées, peux tu élaborer un scenario disruptif pour le secteur de {secteur} à l'horizon {horizon} \
    Pour élaborer un scenario disruptif  tu peux croiser des tendances parmi celles citées en considérant l’environnement dans lequel on se trouvait si ces tendances se réalisaient de manière radicale et :\
    - Il es très important que le scénario généré soit consistant et pas une simple juxtaposition de tendances. Il faut de la cohérence par rapport aux enjeux et la culture du secteur.\
    - imaginer et décrive l’environnement dans lequel on se trouve en {horizon}, en France... Cet environnement est le produit de la réalisation des tendances identifiées. \
    Ces deux tendances se sont trés largement développées. Elles se sont installées.\
    - raconter une courte histoire de ce qui s'est passé pendant une periode de dix ans et qui explique comment, au travers de quels événements, ce scenario s'est installé. \
    Ces événements sont racontés sous la forme de nouvelles (titre de presse et courte accroche, avec date et détail de l’événement)\
    - Décrire la situation qui en résulte pour la société en générale et les entreprises du secteur en particulier, une fois ce scenario installé.\
    - Sois le plus précis possible, essaie de donner des exemples concrets, précis et disruptifs mais très plausibles. Il faut qu'un expert du secteur trouve ce scenario crédible.\
    Précise les tendances choisis pour élaborer le scénario.\
    Donne un titre à ce scenario.\
    <tendances>{res5}</tendances>\n\n{precisions}"

res6 = generate_result(prompt6, "perplexity")

    
prompt6bis = f"Voici un premier scenario développé : \n\n {res6}\n\n{precisions}" + "Peux tu maintenant développer un autre scénario, complètement différent, en te basant sur certaines des tendances citées ou leur inverse (des tendances inverses à celles selectionnées), peux tu élaborer un scenario disruptif pour le secteur de {secteur} à l'horizon {horizon} \
    Pour élaborer ce nouveau scenario disruptif il faut croiser les tendances (ou leur inverse) parmi celles citées (mais sans aboutir à un scénario équivalent au précédent) en considérant l’environnement dans lequel on se trouvait si ces tendances se réalisaient de manière radicale et :\
    - Il es très important que le scénario généré soit consistant et pas une simple juxtaposition de tendances. Il faut qu'il soit crédible. Il faut de la cohérence par rapport aux enjeux et la culture du secteur.\
    - imaginer et décrive l’environnement dans lequel on se trouve en {horizon}, en France... Cet environnement est le produit de la réalisation des tendances identifiées. \
    Ces deux tendances se sont trés largement développées. Elles se sont installées.\
    - raconter une courte histoire de ce qui s'est passé pendant une periode de dix ans et qui explique comment, au travers de quels événements, ce scenario s'est installé. \
    Ces événements sont racontés sous la forme de nouvelles (titre de presse et courte accroche, avec date et détail de l’événement)\
    - Décrire la situation qui en résulte pour la société en générale et les entreprises du secteur en particulier, une fois ce scenario installé.\
    - Sois le plus précis possible, essaie de donner des exemples concrets, précis et disruptifs mais très plausibles. Il faut qu'un expert du secteur trouve ce scenario crédible.\
    Précise les tendances choisis pour élaborer le scénario.\
    Donne un titre à ce scenario.\
    Voici les tendances selectionnées <tendances>{res5}</tendances>"    
res6bis = generate_result(prompt6bis, "perplexity")

print ("### Voici les scenarios" + res6 + "\n\n" + res6bis + "\n\n\n\n\n")


### ARTICLE SCENARIOS   

prompt7 = f"Voici un scénario qui peut changer la donne dans le secteur de {secteur} à l’horizon {horizon}\
<scenario>\
    \n\n{res6}\
</scenario>\
Rédige un article à la manière d’un journaliste expert en prospective qui présente ce scenario . Il faut écrire de façon directe, informative et didactique.  Essaie d'évaluer la probabilité. de ce scénario.  Attention à ne pas être redondant dans tes tournures de phrases. Evite les titres trop longs, l’usage excessif de liste, les doubles adjectifs. Utilise un style incisif.\
Voici la structure d’article que je souhaite que tu utilises. l’article suivant concernait le secteur de l’automobile. Ne prends pas en compte son contenu, base toi sur sa structure et son style pour rédiger l’article sur les scénarios liés au secteur de {secteur} en général.\
<article exemple> \
    Scénario 1 : La grande migration verticale : quand l'habitat s'adapte au climat\
    La transformation radicale de l'habitat français s'annonce comme une réponse inévitable face à l'intensification des chaleurs extrêmes. Un scénario qui prend racine dans les alertes actuelles des experts climatiques.\
    Les catalyseurs du changement. 2026 : L'été de tous les dangers. \
    Paris connaît sa première canicule meurtrière avec des températures dépassant les 45°C pendant deux semaines. Les logements sous les toits deviennent inhabitables, forçant l'évacuation de milliers de résidents (source). La mission 'Paris à 50°C' publie un rapport d'urgence préconisant 85 mesures d'adaptation. \
    2027 : La réponse législative. Face à l'urgence, le Parlement vote la loi sur la verticalisation climatique. Ce texte autorise la transformation des immeubles de bureaux vacants en 'hubs résidentiels climatiques' et impose des normes d'adaptation pour les nouvelles constructions (source).\
    2028 : L'expérimentation lyonnaise. Lyon inaugure le premier méga-hub résidentiel adaptatif. Cette tour de 50 étages devient un modèle de résilience climatique, intégrant des solutions innovantes de rafraîchissement naturel et d'autonomie énergétique.\
    La révolution verticale de 2035\
    Le nouveau standard résidentiel\
    Les hubs climatiques verticaux s'imposent comme la norme dans les métropoles. Ces structures intègrent :\
    Des appartements bioclimatiques modulables\
    Des espaces refuges naturellement tempérés\
    Des systèmes de production alimentaire intégrés\
    Une gestion collective intelligente des ressources\
    Impact sur le marché immobilier\
    Le secteur connaît une mutation profonde. Les promoteurs traditionnels évoluent vers un rôle d'opérateurs de services résidentiels.\
    Évaluation de la probabilité : moyenne à forte\
    Ce scénario s'appuie sur des tendances déjà observables :\
    Facteurs de réalisation\
    Les projections du Haut Conseil pour le Climat anticipent un réchauffement de 4°C en France d'ici la fin du siècle (source).\
    Les épisodes caniculaires s'intensifient, rendant déjà certains logements inhabitables en été (source).\
    La loi Climat et Résilience pose les bases réglementaires de cette transformation (source).\
    Obstacles potentiels\
    Le coût financier de la transformation du parc immobilier\
    La résistance culturelle au modèle communautaire\
    Les contraintes techniques de rénovation\
    Ce scénario, bien que radical, s'inscrit dans la continuité des adaptations nécessaires face au changement climatique. Les événements récents et les projections scientifiques suggèrent une probabilité moyenne à forte de sa réalisation, particulièrement dans les grandes métropoles françaises (source).\
    Voici deux autres tendances qui me semblent importantes et à partir desquelles j’ai imaginé un second scénario.\
    L'émergence de nouveaux modèles d'investissement immobilier\
    L'émergence de nouveaux modèles d'investissement immobilier révolutionne le paysage du secteur. Parmi ces innovations, les plateformes d'investissement immobilier fractionné permettent à un plus grand nombre d'investisseurs de participer au marché immobilier en acquérant des parts de biens, rendant ainsi l'investissement plus accessible. Parallèlement, le coliving se développe comme un modèle attractif pour l'investissement locatif, répondant à la demande croissante pour des solutions de logement flexibles et communautaires. Cette transformation s'accompagne d'une évolution vers des logements considérés comme des actifs plus liquides, facilitée par l'apparition de nouveaux véhicules d'investissement qui offrent des options diversifiées et dynamiques. Ces changements témoignent d'une volonté d'adapter l'investissement immobilier aux nouvelles réalités économiques et sociales.\
    Le rééquilibrage géographique\
    Le rééquilibrage géographique s'affirme comme une tendance significative dans le paysage urbain et rural français, influencée par divers facteurs sociétaux et économiques. Les Jeux Olympiques de 2024, par exemple, pourraient accélérer la gentrification en Seine-Saint-Denis, modifiant ainsi la dynamique de la population dans cette région. Parallèlement, le développement de l'habitat participatif en réhabilitation dans les territoires ruraux, soutenu par l'AMI 2024 de l'ANCT, témoigne d'une volonté de revitaliser ces espaces et d'encourager un nouveau mode de vie. Ce phénomène de déplacement des populations vers les villes moyennes et la grande couronne, en réponse à la hausse des prix dans les grandes métropoles, s'inscrit dans un mouvement de redistribution démographique plus large. Amplifiée par l'essor du télétravail et les nouvelles politiques d'aménagement territorial, cette dynamique transforme profondément les équilibres territoriaux, favorisant un habitat plus inclusif et diversifié.\
</article exemple>\n\n{precisions}"
res7 = generate_result(prompt7, "perplexity")


    
prompt7bis = f"Voici un scénario qui peut changer la donne dans le secteur de {secteur} à l’horizon {horizon}\
<scenario>\
    \n\n{res6bis}\
</scenario>\
Rédige un article à la manière d’un journaliste expert en prospective qui présente ce scenario . Il faut écrire de façon directe, informative et didactique.  Essaie d'évaluer la probabilité. de ce scénario.  Attention à ne pas être redondant dans tes tournures de phrases. Evite les titres trop longs, l’usage excessif de liste, les doubles adjectifs. Utilise un style incisif.\
Voici la structure d’article que je souhaite que tu utilises. l’article suivant concernait le secteur de l’automobile. Ne prends pas en compte son contenu, base toi sur sa structure et son style pour rédiger l’article sur les scénarios liés au secteur de {secteur} en général.\
<article exemple> \
    Scénario 1 : La grande migration verticale : quand l'habitat s'adapte au climat\
    La transformation radicale de l'habitat français s'annonce comme une réponse inévitable face à l'intensification des chaleurs extrêmes. Un scénario qui prend racine dans les alertes actuelles des experts climatiques.\
    Les catalyseurs du changement. 2026 : L'été de tous les dangers. \
    Paris connaît sa première canicule meurtrière avec des températures dépassant les 45°C pendant deux semaines. Les logements sous les toits deviennent inhabitables, forçant l'évacuation de milliers de résidents (source). La mission 'Paris à 50°C' publie un rapport d'urgence préconisant 85 mesures d'adaptation. \
    2027 : La réponse législative. Face à l'urgence, le Parlement vote la loi sur la verticalisation climatique. Ce texte autorise la transformation des immeubles de bureaux vacants en 'hubs résidentiels climatiques' et impose des normes d'adaptation pour les nouvelles constructions (source).\
    2028 : L'expérimentation lyonnaise. Lyon inaugure le premier méga-hub résidentiel adaptatif. Cette tour de 50 étages devient un modèle de résilience climatique, intégrant des solutions innovantes de rafraîchissement naturel et d'autonomie énergétique.\
    La révolution verticale de 2035\
    Le nouveau standard résidentiel\
    Les hubs climatiques verticaux s'imposent comme la norme dans les métropoles. Ces structures intègrent :\
    Des appartements bioclimatiques modulables\
    Des espaces refuges naturellement tempérés\
    Des systèmes de production alimentaire intégrés\
    Une gestion collective intelligente des ressources\
    Impact sur le marché immobilier\
    Le secteur connaît une mutation profonde. Les promoteurs traditionnels évoluent vers un rôle d'opérateurs de services résidentiels.\
    Évaluation de la probabilité : moyenne à forte\
    Ce scénario s'appuie sur des tendances déjà observables :\
    Facteurs de réalisation\
    Les projections du Haut Conseil pour le Climat anticipent un réchauffement de 4°C en France d'ici la fin du siècle (source).\
    Les épisodes caniculaires s'intensifient, rendant déjà certains logements inhabitables en été (source).\
    La loi Climat et Résilience pose les bases réglementaires de cette transformation (source).\
    Obstacles potentiels\
    Le coût financier de la transformation du parc immobilier\
    La résistance culturelle au modèle communautaire\
    Les contraintes techniques de rénovation\
    Ce scénario, bien que radical, s'inscrit dans la continuité des adaptations nécessaires face au changement climatique. Les événements récents et les projections scientifiques suggèrent une probabilité moyenne à forte de sa réalisation, particulièrement dans les grandes métropoles françaises (source).\
    Voici deux autres tendances qui me semblent importantes et à partir desquelles j’ai imaginé un second scénario.\
    L'émergence de nouveaux modèles d'investissement immobilier\
    L'émergence de nouveaux modèles d'investissement immobilier révolutionne le paysage du secteur. Parmi ces innovations, les plateformes d'investissement immobilier fractionné permettent à un plus grand nombre d'investisseurs de participer au marché immobilier en acquérant des parts de biens, rendant ainsi l'investissement plus accessible. Parallèlement, le coliving se développe comme un modèle attractif pour l'investissement locatif, répondant à la demande croissante pour des solutions de logement flexibles et communautaires. Cette transformation s'accompagne d'une évolution vers des logements considérés comme des actifs plus liquides, facilitée par l'apparition de nouveaux véhicules d'investissement qui offrent des options diversifiées et dynamiques. Ces changements témoignent d'une volonté d'adapter l'investissement immobilier aux nouvelles réalités économiques et sociales.\
    Le rééquilibrage géographique\
    Le rééquilibrage géographique s'affirme comme une tendance significative dans le paysage urbain et rural français, influencée par divers facteurs sociétaux et économiques. Les Jeux Olympiques de 2024, par exemple, pourraient accélérer la gentrification en Seine-Saint-Denis, modifiant ainsi la dynamique de la population dans cette région. Parallèlement, le développement de l'habitat participatif en réhabilitation dans les territoires ruraux, soutenu par l'AMI 2024 de l'ANCT, témoigne d'une volonté de revitaliser ces espaces et d'encourager un nouveau mode de vie. Ce phénomène de déplacement des populations vers les villes moyennes et la grande couronne, en réponse à la hausse des prix dans les grandes métropoles, s'inscrit dans un mouvement de redistribution démographique plus large. Amplifiée par l'essor du télétravail et les nouvelles politiques d'aménagement territorial, cette dynamique transforme profondément les équilibres territoriaux, favorisant un habitat plus inclusif et diversifié.\
</article exemple>\n\n{precisions}"
res7bis = generate_result(prompt7bis, "perplexity")


print("#### Voici les article concernant les scénarios" + res7 + "\n\n" + res7bis + "\n\n\n\n\n")


### RESUME SCEN

prompt8 = f"peux tu résumer ce scenario en 3 phrases, sans bullet point. En faire un abstract pour le présenter à un public de non spécialistes. <scenario>{res7}</scenario>\n\n{precisions}"
res8 = generate_result(prompt8, "perplexity")


prompt8bis = f"peux tu résumer ce scenario en 3 phrases, sans bullet point. En faire un abstract pour le présenter à un public de non spécialistes. <scenario>{res7bis}</scenario>\n\n{precisions}"
res8bis = generate_result(prompt8bis, "perplexity")


print("#### Voici les abstracts de scenarios. \n\n SCENARIO 1 : \n" + res8 + "\n\nSCENARIO 2 : \n" + res8bis + "\n\n\n\n\n")


### SWOT ###

prompt9 = f"Immergeons-nous dans un scénario futuriste pour le secteur de {secteur} à l'horizon {horizon}, où nous explorerons les transformations de ce secteur en France et en Europe. Voici un scenario surlequel travailler : {res7}\n{res6}. Imagine un monde où ces changements prennent forme. Quels seraient les risques et les opportunités pour les acteurs de ce secteur ? Utilisons la matrice SWOT pour une analyse fine. Détaille chaque élément de cette matrice par des exemples concrets, en scrutant les forces, les faiblesses, mais aussi les menaces et les opportunités qui pourraient émerger. Sois précis, documente ton argumentaire et pousse la réflexion pour anticiper les impacts tangibles sur l'industrie. Ton analyse doit non seulement esquisser les contours de ce futur possible mais aussi offrir des pistes de réflexion solidement ancrées dans une prospective éclairée et audacieuse.\n\n{precisions}"
res9 = generate_result(prompt9, "perplexity")

prompt9bis = f"Immergeons-nous dans un scénario futuriste pour le secteur de {secteur} à l'horizon {horizon}, où nous explorerons les transformations de ce secteur en France et en Europe. Voici un scenario surlequel travailler : {res7bis}\n{res6bis}. Imagine un monde où ces changements prennent forme. Quels seraient les risques et les opportunités pour les acteurs de ce secteur ? Utilisons la matrice SWOT pour une analyse fine. Détaille chaque élément de cette matrice par des exemples concrets, en scrutant les forces, les faiblesses, mais aussi les menaces et les opportunités qui pourraient émerger. Sois précis, documente ton argumentaire et pousse la réflexion pour anticiper les impacts tangibles sur l'industrie. Ton analyse doit non seulement esquisser les contours de ce futur possible mais aussi offrir des pistes de réflexion solidement ancrées dans une prospective éclairée et audacieuse.\n\n{precisions}"
res9bis = generate_result(prompt9bis, "perplexity")

print("#### Voici les analyses SWOT des scenarios. \n\n SCENARIO 1 : \n" + res9 + "\n\nSCENARIO 2 : \n" + res9bis + "\n\n\n\n\n")


### ACTIONS / PROJETS
prompt10 = f"Imaginons le secteur de {secteur} en {horizon}, et explorons les risques et opportunités qui pourraient se dessiner pour les acteurs clés de ce domaine. Sur la base de ces projections, propose des actions innovantes et réalistes qu'un grand acteur du secteur devrait envisager dès 2025 pour se préparer à ce futur. Pour étayer ta proposition, recherche des initiatives internationales lancées après 2023 par des acteurs de ce secteur, qui pourraient servir de modèle. Utilise ces exemples pour rédiger un article dans le style d'un journalisme d'investigation, en intégrant des exemples supplémentaires d'actions pertinentes et en développant un paragraphe sur des projets spécifiques qui illustrent ces stratégies en action. Voici le scénario à étudier : {res7}\n{res6}. Et voici les résultats de l'analyse SWOT de ce scénario: {res9}.\n\n{precisions}" 
res10 = generate_result(prompt10, "perplexity")

prompt10bis = f"Imaginons le secteur de {secteur} en {horizon}, et explorons les risques et opportunités qui pourraient se dessiner pour les acteurs clés de ce domaine. Sur la base de ces projections, propose des actions innovantes et réalistes qu'un grand acteur du secteur devrait envisager dès 2025 pour se préparer à ce futur. Pour étayer ta proposition, recherche des initiatives internationales lancées après 2023 par des acteurs de ce secteur, qui pourraient servir de modèle. Utilise ces exemples pour rédiger un article dans le style d'un journalisme d'investigation, en intégrant des exemples supplémentaires d'actions pertinentes et en développant un paragraphe sur des projets spécifiques qui illustrent ces stratégies en action. Voici le scénario à étudier : {res7bis}\n{res6bis}. Et voici les résultats de l'analyse SWOT de ce scénario: {res9bis}.\n\n{precisions}" 
res10bis = generate_result(prompt10bis, "perplexity")

print("#### Voici les actions et projets à envisager. \n\n SCENARIO 1 : \n" + res10 + "\n\nSCENARIO 2 : \n" + res10bis + "\n\n\n\n\n")
    
    

