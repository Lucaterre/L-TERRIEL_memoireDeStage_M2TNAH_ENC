"""
Exemple de script pour l'étiquetage morpho-syntaxique (part-of-speech)

Auteur : Lucas Terriel
Date : 14/09/2020
"""

# On importe le package spacy (tâches NLP)
import spacy
from spacy import displacy

# On charge un modèle français
# ! préalable télécharger le modèle (réseau convolutionnel entraîné sur deux corpus, WikiNER et Sequoia) !
# python -m spacy download fr_core_news_sm
model_fr = spacy.load("fr_core_news_sm")

# On défini une phrase de test
test = "Paul Charles Claude demeurant à Paris avec sa femme"

def return_POS(sentence):
    """
    fonction pour tokeniser la phrase et retourner les étiquettes grammaticale
    de chaque token.

    :param sentence: phrase
    :type sentence: str
    :return: token et étiquettes POS
    :type return : list
    """
    # Découpage de la phrase en mots (tokens)
    document = model_fr(sentence)
    # Retourne dans un dictionnaire les tokens (X) -clés- et leurs étiquettes (X.pos_) -valeurs- à partir d'une liste en compréhension
    return [{(X, X.pos_)} for X in document]

# affichage du dictionnaire
print(return_POS(test))

# Pour la visualisation dans le navigateur du POS on défini des paramètres de style
options = {"color": "red", "font": "Source Sans Pro"}

# Visualisation POS dans le navigateur
doc = model_fr(test)
displacy.serve(doc, style="dep", options=options)