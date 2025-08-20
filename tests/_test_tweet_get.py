import requests


def get_json_from_url(url):
    """Récupère le contenu JSON depuis une URL"""
    response = requests.get(url)
    response.raise_for_status()  # Vérifie que la requête a réussi
    return response.json()  # Retourne le contenu JSON


def extract_data_from_item(item):
    """Extrait les informations requises depuis un item du contenu JSON"""
    keys = ["date_published", "name", "content_text", "attachments", "image", "url", "title"]
    extracted = {}
    for key in keys:
        extracted[key] = item.get(key, "N/A")  # Utilise "N/A" si la clé n'est pas trouvée
    return extracted


def save_to_text_file(data, filename="output.txt"):
    """Enregistre les informations dans un fichier texte et retourne le contenu"""
    with open(filename, "w") as file:
        for item_data in data:
            for key, value in item_data.items():
                line = f"{key}: {value}\n"
                file.write(line)
            file.write("\n\n")  # Deux sauts de ligne entre chaque tweet
    with open(filename, "r") as file:
        return file.read()

def main():
    # Remplacez cette URL par l'URL de votre fichier JSON
    url = "https://rss.app/feeds/v1.1/Fz8xd8gGCaB8d4vh.json"

    json_data = get_json_from_url(url)
    items = json_data.get("items", [])
    extracted_data_list = [extract_data_from_item(item) for item in items]
    text_content = save_to_text_file(extracted_data_list)

    print(text_content)

if __name__ == "__main__":
    main()
