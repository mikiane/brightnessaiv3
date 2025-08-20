import fitz  # PyMuPDF
from PIL import Image






def concatenate_images(image_path, footer_path, output_path):
    # Ouvrir les images
    image = Image.open(image_path)
    footer = Image.open(footer_path)

    # Adapter la largeur du footer à celle de l'image principale, en préservant le ratio
    footer_width = image.width
    footer_height = int(footer.height * footer_width / footer.width)
    footer_resized = footer.resize((footer_width, footer_height))

    # Créer une nouvelle image avec la hauteur combinée des deux images
    new_image_height = image.height + footer_resized.height
    new_image = Image.new('RGB', (image.width, new_image_height))

    # Coller l'image principale et le footer dans la nouvelle image
    new_image.paste(image, (0, 0))
    new_image.paste(footer_resized, (0, image.height))

    # Sauvegarder la nouvelle image
    new_image.save(output_path)

    return "Image concaténée créée avec succès"


def pdf_to_png(pdf_path, output_folder):
    # Ouvrir le fichier PDF
    doc = fitz.open(pdf_path)

    # Parcourir chaque page du PDF
    for page_num in range(len(doc)):
        # Obtenir la page
        page = doc.load_page(page_num)

        # Rendre la page en image
        pix = page.get_pixmap()

        # Nom de l'image suivant le format spécifié
        image_name = f"guide_{page_num + 1}.png"

        # Sauvegarder l'image dans le dossier de sortie
        pix.save(f"{output_folder}/{image_name}")
        
        # Chemins des images (exemple)
        image_path = f"{output_folder}/{image_name}"
        footer_path = 'footer3.png'

        # Chemin de sortie de l'image finale
        output_path = f"{output_folder}/_ppp_{image_name}_final.png"
        
        # Appeler la fonction
        result = concatenate_images(image_path, footer_path, output_path)

    # Fermer le document PDF
    doc.close()

    return f"Images sauvegardées dans {output_folder}"



# Chemin du fichier PDF (exemple)
pdf_path = 'guideppp.pdf'

# Chemin du dossier de sortie pour les images
output_folder = 'img'

# Appeler la fonction
result = pdf_to_png(pdf_path, output_folder)
result







