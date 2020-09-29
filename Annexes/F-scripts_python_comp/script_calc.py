"""
Script pour illustrer les différents scores de similarité syntaxique
entre deux chaînes de caractères et leurs implémentations en Python :

* Algorithme Ratcliff/Obershelp
* Distance de Levenshtein
* Word Error Rate (Taux d'erreur de mots)
* Character Error Rate (Taux d'erreur de mots)
* Word Accuracy (Taux de reconnaissance de mots)

! Voir les résultats à la fin du script !

Auteur : Lucas Terriel
Date : 14/09/2020
"""

# On importe le module NLTK pour découper les phrases en mots et en caractères
from nltk import regexp_tokenize

# On importe le module built-in implémentant l'algorithme Ratcliff/Obershelp
import difflib

# On importe la fonction _fast_levenshtein() de l'API Kraken (module lib.dataset)
from kraken.lib.dataset import _fast_levenshtein

# On définit une phrase de référence (Ground Truth) et une prédiction (transcription HTR) de test

reference = "En l'an 1920 par la procuration"

prediction = "En l'an 1920 par le procureur"

# ! Pré-traitements textuels de la phrase de référence (pour le WER et le CER) !

def tokenize_words_char(sequence:str) -> list:
	"""
	* découpage en mots (regex : \W)
	* decoupage en lettres (regex : '')

	sequence (str) : sequence à tokeniser
	return (list) : tokens mots ou caractères
	"""
	tok_mots = regexp_tokenize(sequence, pattern='\W', gaps=True)
	tok_caracteres = regexp_tokenize(sequence, pattern='', gaps=True)
	return tok_mots, tok_caracteres

# Tokenisation de la référence et de la prédiction (au niveau des mots et des caractères)
reference_tok_mots, reference_tok_caracteres = tokenize_words_char(reference)
prediction_tok_mots, prediction_tok_caracteres = tokenize_words_char(prediction)

# calcul du score de similarité avec l'algorithme Ratcliff/Obershelp
similarite_ro = difflib.SequenceMatcher(None, reference, prediction).ratio()

# calcul de la distance de Levenshtein
lev_distance = _fast_levenshtein(reference, prediction)

# calcul du WER (Word Error Rate)
def WER(distance:int, reference_mots :list) -> int:
	"""
	Calcul du Word Error Rate
	WER = Distance(reference,prediction) / nombre_total_mots_référence
	(On donne le résultat en pourcentage et en décimal pour le Word accuracy)
	
	distance (int) : distance d'édition
	reference_mots (list) : phrase découpée en mots
	returns (int) : taux d'erreur de mots (WER) en décimal et en pourcentage
	"""
	resultat = (distance / len(reference_mots))
	resultat_pourcent = (distance / len(reference_mots)) * 100
	return resultat, resultat_pourcent

# Le WER travaille au niveau des mots
resultat_wer_dec, resultat_wer = WER(_fast_levenshtein(reference_tok_mots, prediction_tok_mots), reference_tok_mots)

# calcul du CER (Character Error Rate)
def CER(distance:int, reference_caracteres :list) -> int:
	"""
	Calcul du Word Error Rate
	CER = Distance(reference,prediction) / nombre_total_caracteres_référence
	(On donne le résultat en pourcentage)
	
	distance (int) : distance d'édition
	reference_mots (list) : phrase découpée en caractères
	return (int) : taux d'erreur de caractères en pourcentage (CER)
	"""
	resultat_pourcent = (distance / len(reference_caracteres)) * 100
	return resultat_pourcent

# Le CER travail au niveau des caractères
resultat_cer = CER(lev_distance, reference_tok_caracteres)

# calcul du Word Accuracy (Taux de reconnaissance des mots)
def W_acc(WER:int) -> int:
	"""
	Calcul du Word Accuracy (Taux de reconnaissance des mots)
	W_Acc = (1 - WER) * 100 
	(On donne le résultat en pourcentage)
	
	WER (int) : résultat du WER en décimal
	return (int) : résultat du Word accuracy
	"""
	resultat_pourcent = (1-WER) * 100
	return resultat_pourcent

resultat_wacc = W_acc(resultat_wer_dec)


# On affiche les différents scores :
print(f'Le score de similarité (Ratcliff/Obershelp) est de : {similarite_ro}')
print(f'La distance de Levenshtein est de : {lev_distance}')
print(f'Le CER est de : {resultat_cer} %')
print(f'Le WER est de : {resultat_wer} %')
print(f'Le Word accuracy est de : {resultat_wacc} %')