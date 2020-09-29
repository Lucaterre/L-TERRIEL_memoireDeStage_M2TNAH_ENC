"""
Exemple de script pour afficher les métadonnées EXIF d'une image

Auteur : Lucas Terriel
Date : 14/09/2020
"""

# import du module pyExifTool pour l'extraction de métadonnées Exif
import exiftool

# Création de l'objet ExifTool, on localise l'image et récupération des métadonnées dans un dictionnaire (possibilité de traiter en lot - batch)
with exiftool.ExifTool() as et:
    metadata = et.get_metadata('../static/Voyage_au_centre_de_la_[...]Verne_Jules_btv1b8600259v_16.jpeg')

# Affichage des métadonnées à partir du dictionnaire
for key, value in metadata.items():
    print(f'{key} => {value}')