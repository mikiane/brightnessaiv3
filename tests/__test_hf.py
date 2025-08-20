import lib__hfmodels



API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
#API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
#API_URL = "https://ip3sfgfpf0msnab7.us-east-1.aws.endpoints.huggingface.cloud"
MAX_TOKEN = 100
API_TOKEN = "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"
#CONSIGNE = str("Objectif, obtenir une liste de points clés contenus dans le texte suivant. Tache, extraire les points clés du texte suivant sous forme de liste de points. Format, sous la forme d'une liste contenant des tirets et des sauts à la ligne décrivant chaque point extrait du texte.")
CONSIGNE = "Proposer des synonymes pour le mot suivant :"
#TEXTE = str("Après Ciaran, la tempête Domingos secoue la France et occasionne de nombreux dégâts sur le réseau ferroviaire  Treize départements sont en alerte orange, dimanche matin, alors qu’Enedis a annoncé la mort d’un de ses salariés, mobilisé après le passage de la tempête Ciaran.\n\nDeux jours après Ciaran, une nouvelle tempête baptisée Domingos a fait irruption, samedi 4 novembre, sur la France, déjà éprouvée par les intempéries. Du Pas-de-Calais à la Méditerranée et la Corse, en passant par la façade atlantique et la Nouvelle-Aquitaine, treize départements sont, dimanche, en alerte orange aux fortes vagues et aux crues. Dans son bulletin de 6 heures du matin, dimanche, Météo-France a, en revanche, levé les alertes orange pour vent et pour pluie-inondation.\n\nDomingos, a priori *« moins sévère »* que sa devancière, selon Météo-France, pourrait toutefois causer de nouveaux dégâts dans des zones déjà touchées par Ciaran, qui a fait en France au moins trois morts et des dizaines de blessés. Dimanche matin, Enedis a annoncé la mort d’une quatrième personne, un de ses salariés, dans un accident, alors qu’il était mobilisé en Bretagne, à Pont-Aven, après le passage de la tempête Ciaran.\n\nCette nouvelle dépression devrait compliquer et ralentir les réparations du réseau électrique, toujours en cours, selon Enedis, qui faisait état, samedi à 18 h 30, de 176 000 clients privés de courant depuis jeudi, notamment en Bretagne et en Normandie, contre 260 000 à 8 heures.\n\nDimanche, peu après minuit, 22 800 foyers n’avaient ainsi plus accès à l’électricité, selon une publication sur X (anciennement Twitter) du préfet de Nouvelle-Aquitaine et de la Gironde. A l’échelle de la Vienne, ce nombre s’élevait à 3 000 tôt dimanche, a écrit sur X le préfet du département.\n\n13 départements en vigilance orange\n\nCette carte montre le niveau de vigilance météorologique et les risques de crues par département.\n\nÇa souffle\n\n*Le centre dépressionnaire lié à la tempête Domingos s’est décalé en mer du Nord*, **explique Météo-France. *Sur le pays, le temps reste agité avec de fréquentes averses ; les rafales qui les accompagnent sont moins fortes, perdant leur caractère tempétueux.*\n\nAprès les vents record de Ciaran, mercredi et jeudi − jusqu’à 207 km/h à la pointe du Raz, dans le Finistère −, l’institut météorologique a enregistré, samedi en soirée, des vents à 152 km/h à Lège-Cap-Ferret (Gironde), 144 km/h à Cognac (Charente), 138 km/h à Rochefort (Charente-Maritime) ou encore 136 km/h à Niort.\n\n*Ça souffle*, a confirmé, à l’Agence France-Presse (AFP), Lionel Quillet, maire de Loix sur l’île de Ré (Charente-Maritime). Mais, *avec un coefficient de marée* assez bas de 40, on ne devrait pas avoir le risque de submersion. On a un niveau de protection assez élevé, même si le risque zéro n’existe pas.*\n\nLe passage de la tempête Domingos a occasionné de nombreux dégâts sur le réseau ferroviaire en Nouvelle-Aquitaine et provoqué des retards considérables pour deux trains de la ligne Paris-Orléans-Limoges-Toulouse (POLT). Les passagers ont dû passer la nuit en gare de Brive, a annoncé la SNCF dimanche. Du côté de La Rochelle, *« de nombreux arbres sont couchés sur les voies »* et, en Vendée, *« ce sont les feuilles qui ont recouvert les rails, posant des risques de difficultés")
TEXTE = "Maison"
NUM_TOKENS = 1500
PROMPT = CONSIGNE + "\n Le texte : ### " + TEXTE + " ###\n"
# Créer une instance du générateur
generator_instance = lib__hfmodels.stream_hfllm(PROMPT, API_TOKEN, API_URL, MAX_TOKEN, NUM_TOKENS)

# Itérer sur le générateur pour exécuter et obtenir les valeurs
for generated_text in generator_instance:
    print(generated_text)
    
    
    
    
