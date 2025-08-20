import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Import des classes et outils LangChain
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

##############################################
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
##############################################
load_dotenv(".env")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_TOKEN")
GOOGLE_CSE_ID = os.environ.get("CSE_ID")
OPENAI_API_KEY = os.environ.get("OPEN_AI_KEY")

##############################################
# CRÉATION DU LLM AVEC LA NOUVELLE API
##############################################
chat_llm = ChatOpenAI(
    temperature=1,
    model_name="gpt-3.5-turbo",  # ou "gpt-4"
    openai_api_key=OPENAI_API_KEY,
)

##############################################
# DÉFINITION DES PROMPTS
##############################################
prompt_step1 = PromptTemplate(
    input_variables=["sector", "horizon"],
    template="""
    Vous êtes un expert en prospective et en tendances économiques.
    Pour le secteur suivant: {sector} et à l'horizon temporel suivant: {horizon}, 
    identifiez les principales tendances émergentes qui pourraient influencer ce secteur.

    Listez plusieurs tendances et expliquez en quelques mots leur impact potentiel.
    """
)

prompt_step2 = PromptTemplate(
    input_variables=["tendances"],
    template="""
    Les tendances suivantes ont été identifiées:
    {tendances}

    À partir de cette liste, sélectionnez et justifiez les deux tendances 
    qui sont à la fois les plus impactantes et les plus plausibles pour le secteur. 
    """
)

prompt_step3 = PromptTemplate(
    input_variables=["tendance1", "tendance2", "sector"],
    template="""
    Vous êtes un expert en prospective. 
    Imaginez un scénario à l'horizon 2030 (ou l’horizon choisi) où les deux tendances suivantes 
    se concrétisent simultanément pour le secteur {sector} :
    1) {tendance1}
    2) {tendance2}

    Décrivez ce scénario, racontez l'évolution globale et ses conséquences 
    pour les acteurs de ce secteur.
    """
)

prompt_step4 = PromptTemplate(
    input_variables=["scenario"],
    template="""
    Sur la base du scénario suivant:
    {scenario}

    Proposez une stratégie Blue Ocean complète pour que les acteurs du secteur 
    puissent saisir les opportunités et déjouer les risques liés à ce scénario.
    """
)

prompt_step6 = PromptTemplate(
    input_variables=[
        "sector", 
        "horizon", 
        "tendances", 
        "tendance1", 
        "tendance2", 
        "scenario", 
        "blue_ocean", 
        "web_results"
    ],
    template="""
    Rédigez un article clair et concis intégrant tous les éléments clés :
    - Secteur : {sector}
    - Horizon : {horizon}
    - Tendances identifiées : {tendances}
    - Deux tendances retenues : {tendance1} et {tendance2}
    - Scénario prospectif : {scenario}
    - Stratégie Blue Ocean : {blue_ocean}
    - Exemples de projets réels (via recherche web) : {web_results}

    Assurez-vous que l'article soit rédigé de façon à informer un public professionnel.
    """
)

##############################################
# CHAÎNES LLM
##############################################
chain_step1 = LLMChain(
    llm=chat_llm,
    prompt=prompt_step1,
    output_key="tendances_output"
)

chain_step2 = LLMChain(
    llm=chat_llm,
    prompt=prompt_step2,
    output_key="top2_output"
)

chain_step3 = LLMChain(
    llm=chat_llm,
    prompt=prompt_step3,
    output_key="scenario_output"
)

chain_step4 = LLMChain(
    llm=chat_llm,
    prompt=prompt_step4,
    output_key="blue_ocean_output"
)

##############################################
# IMPLÉMENTATION DE LA RECHERCHE GOOGLE
##############################################
def google_search(query: str, api_key: str = GOOGLE_API_KEY, cse_id: str = GOOGLE_CSE_ID, num: int = 5) -> str:
    """
    Effectue une recherche Google en utilisant l'API Custom Search
    et renvoie les titres + liens pertinents en texte brut.
    """
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num).execute()

    if 'items' not in res:
        return "Aucun résultat trouvé pour la requête."

    results_summary = []
    for item in res['items']:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        results_summary.append(f"• Titre: {title}\n  Lien: {link}\n  Extrait: {snippet}\n")

    return "\n".join(results_summary)

web_search_tool = Tool(
    name="google_web_search",
    func=google_search,
    description="Utilise l'API Google Custom Search pour effectuer une recherche et retourner les résultats sous forme de résumé."
)

##############################################
# INITIALISATION DE L'AGENT LANGCHAIN
##############################################
tools = [web_search_tool]

agent = initialize_agent(
    tools=tools,
    llm=chat_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

##############################################
# ÉTAPE 5 : RECHERCHE DE PROJETS
##############################################
def step5_search_projects(strategy_text: str, sector: str):
    """
    Construit une requête de recherche à partir de la stratégie et du secteur,
    puis utilise l'agent pour obtenir des résultats depuis Google.
    """
    query = f"Projets existants ou initiatives qui mettent en œuvre la stratégie suivante dans le secteur {sector}: {strategy_text}"
    search_result = agent.run(query)
    return search_result

##############################################
# ORCHESTRATION
##############################################
def generate_prospective_article(sector: str, horizon: str):
    """
    Orchestration globale des 6 étapes pour générer un article prospectif.
    """
    # Étape 1 : Identifier les tendances émergentes
    tendances_result = chain_step1.run({"sector": sector, "horizon": horizon})
    print("\n=== Étape 1: Tendances émergentes ===")
    print(tendances_result)

    # Étape 2 : Sélectionner 2 tendances les plus impactantes
    top2_result = chain_step2.run({"tendances": tendances_result})
    print("\n=== Étape 2: Deux tendances clés ===")
    print(top2_result)

    # Parsing simple des tendances
    lines = top2_result.strip().split("\n")
    tendance1 = lines[0] if len(lines) > 0 else "Tendance 1 non trouvée"
    tendance2 = lines[1] if len(lines) > 1 else "Tendance 2 non trouvée"

    # Étape 3 : Générer le scénario
    scenario_result = chain_step3.run({
        "tendance1": tendance1,
        "tendance2": tendance2,
        "sector": sector
    })
    print("\n=== Étape 3: Scénario prospectif ===")
    print(scenario_result)

    # Étape 4 : Générer la stratégie Blue Ocean
    blue_ocean_result = chain_step4.run({"scenario": scenario_result})
    print("\n=== Étape 4: Stratégie Blue Ocean ===")
    print(blue_ocean_result)

    # Étape 5 : Recherche web de projets réels
    web_search_results = step5_search_projects(blue_ocean_result, sector)
    print("\n=== Étape 5: Résultats de recherche web ===")
    print(web_search_results)

    # Étape 6 : Générer l'article final
    article_prompt = prompt_step6.format(
        sector=sector,
        horizon=horizon,
        tendances=tendances_result,
        tendance1=tendance1,
        tendance2=tendance2,
        scenario=scenario_result,
        blue_ocean=blue_ocean_result,
        web_results=web_search_results
    )
    final_article = chat_llm.predict(article_prompt)
    print("\n=== Étape 6: Article final ===")
    print(final_article)
    return final_article

##############################################
# EXÉCUTION DU SCRIPT
##############################################
if __name__ == "__main__":
    sector_to_analyze = "Energie renouvelable"
    horizon_time = "2030"

    article = generate_prospective_article(sector_to_analyze, horizon_time)

    # Sauvegarde du résultat
    with open("article_prospectif.txt", "w", encoding="utf-8") as f:
        f.write(article)
