from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv


load_dotenv(".env") # Load the environment variables from the .env file.
endpoint_url = os.getenv("HF_API_KEY")
hf_token = os.getenv("HF_URL")

# Streaming Client
client = InferenceClient(endpoint_url, token=hf_token)

# generation parameter
gen_kwargs = dict(
    max_new_tokens=512,
    top_k=30,
    top_p=0.1,
    temperature=0.001,
    repetition_penalty=1.0,
    stop_sequences=["\nUser:", "<|endoftext|>", "</s>"],
)
# prompt
question = "Propose moi 3 articles correspondant à tes sujets de prédilection en rédigeant la réponse"
contexte = "Contact Préparons ensemble la TEDx Paris : proposez votre Best Of ! La première TEDx Paris aura lieu en mai prochain. Vous êtes déja plus d'une centaine à avoir rejoint le groupe sur Facebook et je reçois beaucoup de messages positifs. Il est temps de commencer à rentrer dans le bain... Je vous invite à faire un tour sur la liste complète des talks depuis leur toute première publication. Sur la base de cette liste, pour voir un TED, il suffit d'effectuer une recherche sur le titre du talk dans Google. Par exemple : pour rechercher le talk « La Vie en Rose » il suffit de saisir dans Google site:ted.com «la vie en rose» Préparons ensemble la première session en partageant nos TED préférés. Cela nous permettra de constituer les premiers items du catalogue de projection de la première session. Il vous suffit pour cela d'indiquer en commentaire juste en dessous quel(s) talk(s) vous appréciez ou de poster un message sur le wall du groupe TEDx Paris. Voici ma liste préférée... The paradox of choice A surprising parable of foie gras Why are we happy? Why aren't we happy? Why people believe strange things La Vie en Rose Why design? One Laptop per Child, two years on BilletMichel LEVY-PROVENCAL31 mars 2009 Facebook0 Twitter LinkedIn0 0 Likes Précédent Créativiste ou Capitaliste? BilletMichel LEVY-PROVENCAL10 mai 2009 Suivant Des TED Camp prochainement à Paris! "
prompt = question + "\n" + "prendre en compte le contexte suivant pour répondre :" + contexte + "\n"

stream = client.text_generation(prompt, stream=True, details=True, **gen_kwargs)

# yield each generated token
for r in stream:
    # skip special tokens
    if r.token.special:
        continue
    # stop if we encounter a stop sequence
    if r.token.text in gen_kwargs["stop_sequences"]:
        break
    # yield the generated token
    print(r.token.text, end = "")
    # yield r.token.text