from dotenv import load_dotenv
import os
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

# Load environment variables
load_dotenv('.env')
APP_PATH = os.environ['APP_PATH']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

import re

# Function to clean and format text for Markdown
def clean_and_format_for_markdown(text):
    # Remove non-standard characters while keeping Markdown formatting
    # Allow letters, numbers, basic punctuation, and markdown symbols
    cleaned_text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\*\#\(\)\[\]\'\"\`\~\>\<\+\=\@\^\&]', '', text)
    # Optional: further processing to convert to Markdown or clean text can be added here
    return cleaned_text

# Modified split_text_into_blocks function
def split_text_into_blocks(text, limit=4000):
    # First, clean and format the text for Markdown
    text = clean_and_format_for_markdown(text)
    
    blocks = []
    current_block = ""
    words = text.split()

    for word in words:
        if len(current_block + word) + 1 < limit:
            current_block += word + " "
        else:
            last_delimiter_index = max(current_block.rfind(". "), current_block.rfind("\n"))
            if last_delimiter_index == -1:
                blocks.append(current_block.strip())
                current_block = word + " "
            else:
                delimiter = current_block[last_delimiter_index]
                blocks.append(current_block[:last_delimiter_index + (1 if delimiter == '.' else 0)].strip())
                current_block = current_block[last_delimiter_index + (2 if delimiter == '.' else 1):].strip() + " " + word + " "

    if current_block.strip():
        blocks.append(current_block.strip())
    return blocks

# Example usage
with open('fireup.txt', 'r', encoding='utf-8') as file:
    text = file.read()
text_segments = split_text_into_blocks(text)

# Now, text_segments will contain cleaned and markdown-formatted text blocks

def extract_context(text, model):
    token_nb = 2000
    
    if model == "claude-2":
        token_nb = 100000 
    if model == "claude-3":
        token_nb = 150000
    if model == "gpt-4":
        token_nb = 8000
    if model == "gpt-4-turbo-preview":
        token_nb = 128000
    if model == "gpt-4-turbo":
        token_nb = 128000
    if model == "gpt-4o":
        token_nb = 250000
    if model == "gpt-3.5-turbo-16k": 
        token_nb = 16000
    if model == "hf":
        token_nb = 2000  
    if model == "mistral":
        token_nb = 2000      
    
    if token_nb > 2000:
        limit = (int(token_nb)*2) - 4000
    else:
        limit = int((int(token_nb)*2)/2)
    
    if len(text) < limit:
        return text
    else:
        half_limit_adjusted = limit // 2 - 4
        return text[:half_limit_adjusted] + ' [...] ' + text[-half_limit_adjusted:]

# Vectorization of text segments
def get_embeddings(texts):
    embeddings = []
    for text in texts:
        text = text.replace("\n", " ")
        response = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
        response_dict = response.model_dump()  # Conversion de la réponse en dictionnaire
        embeddings.append(response_dict['data'][0]['embedding'])
    return np.array(embeddings)

embeddings = get_embeddings(text_segments)

# Clustering based on cosine similarity
similarity_matrix = cosine_similarity(embeddings)
clustering_model = AgglomerativeClustering(n_clusters=None, affinity='precomputed', linkage='average', distance_threshold=0.14)
labels = clustering_model.fit_predict(1 - similarity_matrix)

# Display the number of detected clusters
unique_clusters = np.unique(labels)
print(f"Nombre d'idées détectés : {len(unique_clusters)}")

# Identification of clusters and association of texts
clusters = {}
for label, text in zip(labels, text_segments):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(text)

# Summary of texts in each cluster
for cluster_id, texts in clusters.items():
    cluster_text = " ".join(texts)
    print(f"Idée {cluster_id} :")
    cluster_text = extract_context(cluster_text, "gpt-4o")
    response = openai.chat.completions.create(
      model="gpt-4-turbo",
      messages=[{"role": "system", "content": "Résumer le texte suivant en français et donner un titre au résumé. Ne pas mentionner le terme 'texte' ou 'résumé' dans le contenu produit :"},
                {"role": "user", "content": cluster_text}],
      temperature=0,
      max_tokens=4000,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    summary = response.choices[0].message.content.strip()
    print(f"Résumé: {summary}\n\n")
