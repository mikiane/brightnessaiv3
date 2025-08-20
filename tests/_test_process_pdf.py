import PyPDF2
import sys
import os
from libs import lib__agent_buildchronical

# Utilisez les fonctions ou classes de libx comme vous le feriez normalement


def tweet_gen(text, num_page, command, model="gpt-4-turbo-preview", input_data = "", site = ""):
    # Votre traitement ici
    prompt = command + "\n ___ Voici le texte de la page numero : " + str(num_page) + "\n\n" + text + "\n ___ \n"
    print("Prompt : " + prompt)
    input_data = ""
    site = ""
    model=model
    res = lib__agent_buildchronical.execute(prompt, site, input_data, model)
    print("Traitement de la page : ", text)
    return res

def process_pdf(chemin_du_fichier, command):
    try:
        # Ouvrir le fichier PDF
        res = ""
        with open(chemin_du_fichier, 'rb') as fichier:
            lecteur_pdf = PyPDF2.PdfReader(fichier)
            num_page = 0
            # Itérer sur chaque page
            for page in lecteur_pdf.pages:
                contenu = page.extract_text()
                num_page += 1
                # Appeler la fonction f sur le contenu de la page
                res = res + "\n\n" + tweet_gen(contenu, num_page, command, model="gpt-4-turbo-preview")
                
    except Exception as e:
        print("Une erreur est survenue : ", e)
        
    return res

# Utiliser la fonction
command = "A partir du texte suivant, rédiger un tweet en français pour présenter le texte. Attention à varier les formules (utiliser les termes 'découvrir' ou 'plonger dans' ou 'télécharger le guide' ou 'parcourir' ou utiliser d'autres tournures au choix. Une seule tournure par tweet. Etre créatif dans la manière de tourner les phrases). Utiliser un ton neutre. Etre synthétique. Citer le numero de la page."
chemin_du_fichier = 'guideppp.pdf'
result = process_pdf(chemin_du_fichier, command)
print(result)
with open('tweets_guide_ppp.txt', 'w') as file:
    # Écrire le contenu dans le fichier
    file.write(result)