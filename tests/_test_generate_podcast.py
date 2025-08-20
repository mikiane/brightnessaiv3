
import libs.lib__transformers as lib__transformers

text = "Pour enlever l'intro et l'outro du résultat final, vous pouvez simplement commenter ou supprimer les lignes qui ajoutent ces segments au fichier audio combiné. En outre, vous pouvez également initialiser la variable combined comme un objet AudioSegment vide au lieu de l'introduire avec un fichier intro. Voici à quoi cela pourrait ressembler"
filename = lib__transformers.synthesize_multi(text)
