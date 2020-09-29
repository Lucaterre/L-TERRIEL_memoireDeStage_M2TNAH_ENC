#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Lucas Terriel
#
# Syntactic/Semantic To Similarity - SynSemTS module
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# Syntactic/Semantic To Similarity - SynSemTS is a module
# and a part of large Sequences to Similarity Tools (STS Tools) mini library
# implemented in Kraken-Benchmark application.
# its goal is to propose a set of metrics and
# visualizations to assess the syntactic and semantic similarity approach
# between a reference sentence and a prediction sentence and evaluate a transcription model in
# the context of an Handwritten Text Recognition (HTR) project from:
#
# --| SYNTACTIC METRICS |--
#
# * Ratcliff/Obershelp similarity & histogram
# * Levenshtein distance index & reference versus prediction visualization
# * Word Error Rate (WER)
# * Character Error Rate (CER)
# * Word accuracy
#
# --| SEMANTIC METRICS |--
#
# * Jaccard index
# * Cosine similarity
#
# the library SynTS also offers options for
# pre-processing text
# (punctuation and numbers cleaning steps, tokenization, stop words removing).

"""Syntactic/Semantic To Similarity - SynSemTS

Author : Lucas Terriel
Date : 22/07/2020

# TODO(Lucas) : delete edit distance matrix compute for wer and cer
"""

# built-in packages
import decimal
import os
import re
import math
import string
import difflib
from collections import Counter, defaultdict

# external packages
from kraken.lib.dataset import _fast_levenshtein
from Levenshtein import distance, hamming, editops
import matplotlib.pyplot as plt
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import regexp_tokenize, word_tokenize
from nltk.corpus import stopwords
import numpy as np
from numpy import zeros
import pandas as pd
import seaborn as sn


# MIX OF USEFUL TOOLS FOR SynSemTS

# Text data pre-processing tools

REMOVE_PUNCTUATION_MAP = dict((ord(char), None) for char in string.punctuation)


def normalize(sequence: str) -> list:
    """Tokenize and clean sentence with NLTK tokenizer. Use it for semantic similarity metrics :
    - cosine similarity
    - jaccard index

    Note
    ----

    * tokenize words
    * remove punctuation
    * char lower

    Example
    --------
    >>> sentence = "Un monstre,  aux tentacules géants !"
    >>>            "Et qui entraînent les navires dans les ténebres abyssales."
    >>> normalize(sentence)
    ['un', 'monstre', 'aux', 'tentacules', 'géants', 'et', 'qui',
    'entraînent', 'les', 'navires', 'dans', 'les', 'ténebres', 'abyssales']

    Args:
        sequence (str): string to tokenize and clean

    Returns:
        list: list of tokens words
    """
    return word_tokenize(sequence.lower().translate(REMOVE_PUNCTUATION_MAP))


def clean_text(text: str) -> str:
    """option to performs a few cleanning steps to remove non-alphabetic characters
    use this one for syntaxic similarity metrics if the project necessites
    remove punctuation and space for :

    # TODO(Lucas): to improve and distinguish numbers and punctuation

    - WER
    - CER

    Example
    --------
    >>> sentence = "On dit en 1879 que la puanteur...de son souffle, est moribonde"
    >>> clean_text(sentence)
    On dit en  que la puanteurde son souffle est moribonde

    Args:
        text (str): text to clean

    Returns:
        str: clean text
    """

    # replace new line and carriage return with nothing
    text = text.replace("\n", "").replace("\r", " ")

    # replace the numbers and punctuation  with space
    punc_list = '!"#$%&()*+,-—./:;<=>«»?@[\]^_{|}~\'`’' + '0123456789'
    text_without_punct = str.maketrans(dict.fromkeys(punc_list, ""))
    text = text.translate(text_without_punct)
    return text


def tokenizer(sentence: str, *args: bool) -> list:
    """another regex-based tokenizer works in conjunction with the text
    clean_text() function. returns tokens characters based and words based.

    Example
    --------
    >>> sentence = 'Un homme à la mer !'
    >>> tokenizer(sentence)
    (['Un', 'homme', 'à', 'la', 'mer'],
    ['U', 'n', ' ', 'h', 'o', 'm', 'm', 'e', ' ', 'à', ' ', 'l', 'a', ' ', 'm', 'e', 'r', ' ', '!'])

    Args:
        sentence (str) : sentence to tokenize
        *args (bool) : if user activate clean_text() function option

    Returns:
        list: words-tokens based
        list: character-tokens based
    """

    if args:
        # Use NLTK Package for word cutouts (with space)
        sentence_tokenize_words = regexp_tokenize(clean_text(sentence), pattern='\W', gaps=True)
        # character cutouts (with space)
        sentence_tokenize_characters = regexp_tokenize(clean_text(sentence), pattern='', gaps=True)
    else:
        sentence_tokenize_words = regexp_tokenize(sentence, pattern='\W', gaps=True)
        sentence_tokenize_characters = regexp_tokenize(sentence, pattern='', gaps=True)

    return sentence_tokenize_words, sentence_tokenize_characters

# Metric tool result arrangement

def truncate(result: float) -> int:
    """truncate the result to 2 digits after the decimal point (does not display zeros)

    Example
    --------

    >>> truncate(6.546403)
    6.54
    >>> truncate(15.498452)
    15.49

    Args:
        result (float) : operation result to tokenize

    Returns:
        int : result truncate
    """
    result_truncate = float(decimal.Decimal(result).quantize(decimal.Decimal('.01'),
                                                             rounding=decimal.ROUND_DOWN))
    return result_truncate


def show_diff_color_html(reference: str, prediction: str) -> list:
    """Display source and prediction in HTML format and color-code insertions (blue),
    deletions (red), and exact words (green). based on Levensthein algorithm.

    Example
    --------
    >>> show_diff_color_html("Chat", "Chien")
    ["<span style='color:#3CB371'>C</span>", "<span style='color:#3CB371'>h</span>",
    "<span style='color:#4169E1'>i</span>", "<span style='color:#4169E1'>e</span>",
    "<span style='color:#D2122E'>a</span>", "<span style='color:#4169E1'>n</span>",
    "<span style='color:#D2122E'>t</span>"]

    Args:
        reference (str): reference sequence
        prediction (str): prediction sequence

    Returns:
        list: list of HTML tag with color code
    """
    result = []

    # compute distance
    distance = zeros((len(prediction) + 1, len(reference) + 1), dtype=int)
    distance[0, 1:] = range(1, len(reference) + 1)
    distance[1:, 0] = range(1, len(prediction) + 1)
    for char_pred in range(1, len(prediction) + 1):
        for char_ref in range(1, len(reference) + 1):
            delt = 1 if prediction[char_pred - 1] != reference[char_ref - 1] else 0
            distance[char_pred, char_ref] = min(distance[char_pred - 1, char_ref - 1] + delt,
                                                distance[char_pred - 1, char_ref] + 1,
                                                distance[char_pred, char_ref - 1] + 1)

    # sequences alignment
    # iterate the matrix's values from back to forward
    char_pred = len(prediction)
    char_ref = len(reference)
    while char_pred > 0 and char_ref > 0:
        diagonal = distance[char_pred - 1, char_ref - 1]
        upper = distance[char_pred, char_ref - 1]
        left = distance[char_pred - 1, char_ref]

        # check back direction
        direction = "\\" if diagonal <= upper and \
                            diagonal <= left else "<-" \
            if left < diagonal and \
               left <= upper else "^"
        char_pred = char_pred - 1 if direction == "<-" or direction == "\\" else char_pred
        char_ref = char_ref - 1 if direction == "^" or direction == "\\" else char_ref

        # Colorize characters with HTML tags
        if (direction == "\\"):
            if distance[char_pred + 1, char_ref + 1] == diagonal:
                result.append(f"<span style='color:#3CB371'>{prediction[char_pred]}</span>")
            elif distance[char_pred + 1, char_ref + 1] > diagonal:
                result.append(f"<span style='color:#D2122E'>{reference[char_ref]}</span>")
                result.append(f"<span style='color:#4169E1'>{prediction[char_pred]}</span>")
            else:
                result.append(f"<span style='color:#4169E1'>{prediction[char_pred]}</span>")
                result.append(f"<span style='color:#D2122E'>{reference[char_ref]}</span>")
        elif (direction == "<-"):
            result.append(f"<span style='color:#4169E1'>{prediction[char_pred]}</span>")
        elif (direction == "^"):
            result.append(f"<span style='color:#D2122E'>{reference[char_ref]}</span>")

    # reverse the list of result
    return result[::-1]


class RecognizerTypeFiles:
    """A class for group and identify different types of file

    Attributes:
        source (str) : reference sequence
        prediction (str) : prediction sequence
        source_tokens_words (list) : reference words tokens-based (optionnal with clean text)
        source_tokens_char (list) : reference char tokens-based (optionnal with clean text)
        pred_tokens_words (list) : prediction words tokens-based (optionnal with clean text)
        pred_tokens_char (list) : prediction char tokens-based (optionnal with clean text)
        image (str) : path to image
        name_image (str) : basename image
        canevas_image (str) : html canevas for rendering image
    """

    def __init__(self, source: str, prediction: str, image: str, *args: bool) -> None:
        """Constructs a file cluster to identify differents
        type of text and image forms

        Args:
            source (str): reference sentence
            prediction (str) : prediction sentence
            image (str) : path to image
            *args (bool, optional) : to activate clean mode
        """
        self.source = source
        self.prediction = prediction

        if args:
            clean_mode = args[0]
            self.source_tokens_words, self.source_tokens_char = tokenizer(source, clean_mode)
            self.pred_tokens_words, self.pred_tokens_char = tokenizer(prediction, clean_mode)
        else:
            self.source_tokens_words, self.source_tokens_char = tokenizer(source)
            self.pred_tokens_words, self.pred_tokens_char = tokenizer(prediction)

        #self.colorful_source_prediction_words_html =
        # show_diff_color_html(self.source, self.prediction)

        self.image = image
        self.name_image = os.path.basename(image)
        self.canevas_image = f'<img src="/static/./{self.name_image}" class="img-thumbnail"/>'


def lev_distance(reference: str, hypothesis: str) -> list:
    """calculates the editing distance. The Levensthein algorithm used corresponds to
        that used in dynamic programming. it allows an approach of the word error rate.

        Note
        ----
        based on WER-in-python program (Github @zszyellow)
        more informations : Algorithm implementation of Levenshtein distance
        in Wikibooks

        Example
        -------
        >>> lev_distance("Chien", "Chat")
        [[0 1 2 3 4]
         [1 0 1 2 3]
         [2 1 0 1 2]
         [3 2 1 1 2]
         [4 3 2 2 2]
         [5 4 3 3 3]]

         Args:
            reference (str) : reference sequence
            hypothesis (str) : predicted sequence

        Returns:
            list : sparse matrix
        """
    distance = np.zeros((len(reference) + 1) * (len(hypothesis) + 1), dtype=np.uint8).reshape \
        ((len(reference) + 1, len(hypothesis) + 1))
    for i in range(len(reference) + 1):
        distance[i][0] = i
    for j in range(len(hypothesis) + 1):
        distance[0][j] = j
    for i in range(1, len(reference) + 1):
        for j in range(1, len(hypothesis) + 1):
            if reference[i - 1] == hypothesis[j - 1]:
                distance[i][j] = distance[i - 1][j - 1]
            else:
                substitute = distance[i - 1][j - 1] + 1
                insert = distance[i][j - 1] + 1
                delete = distance[i - 1][j] + 1
                distance[i][j] = min(substitute, insert, delete)
    return distance

class FilesToMetrics(RecognizerTypeFiles):
    """A child class of different kinds of edit distance
    * matrix
    * int
    uses for differents type of syntaxics metrics

    Attributes:
        source (str) : reference sequence
        prediction (str) : prediction sequence
        group_to_distance (object) : RecognizerTypeFiles object
        edit_distance_words_matrix (list) : edit distance use dynamic programming
            algorithm based on numpy
        edit_distance_char_int (list) : edit distance use classic
            algorithm characters based - kraken function
        edit_distance_word_int (list) : edit distance use classic
            algorithm words tokens based  - kraken function
    """

    def __init__(self, source: str, prediction: str, image: str, *args: bool) -> None:
        """
        Constructs a differents types of edit distance
        (results -> matrix, integer)


        Args:
            source (str): reference sequence
            prediction (str) : prediction sequence
            image (str) : path to image
            *args (bool, optional) : activate clean text mode
        """
        RecognizerTypeFiles.__init__(self, source, prediction, image, *args)
        self.source = source
        self.prediction = prediction
        self.group_to_distance = RecognizerTypeFiles(source, prediction, image, *args)
        self.edit_distance_words_matrix = lev_distance(self.group_to_distance.source_tokens_words,
                                                       self.group_to_distance.pred_tokens_words)
        self.edit_distance_char_int = _fast_levenshtein(self.group_to_distance.source_tokens_char,
                                                        self.group_to_distance.pred_tokens_char)
        self.edit_distance_word_int = _fast_levenshtein(self.group_to_distance.source_tokens_words,
                                                        self.group_to_distance.pred_tokens_words)


class TranscriptionMetricsTools(FilesToMetrics):
    """A child class for elaborate metrics on transcription model

    Attributes:
        group_to_metrics (object) : FilesToMetrics object
        source (str) : reference sequence
        prediction (str) : prediction sequence
        distance_matrix_words (list) : edit distance use dynamic programming
            algorithm based on numpy
        distance_int_char (int) : edit distance use classic
            algorithm characters tokens based - kraken function
        distance_int_word (int) : edit distance use classic
            algorithm words tokens based - kraken function
        reference_tokens_words (list) : reference words tokens-based (optionnal with clean text)
        hypothesis_tokens_words (list) : prediction words tokens-based (optionnal with clean text)
        reference_tokens_char (list) : reference char tokens-based (optionnal with clean text)
        hypothesis_tokens_char (list) : prediction char tokens-based (optionnal with clean text)
        stop_words (list) : list of stop words. define language in constructor method
        get_sequence_stop (function) : supress words stops on the fly
        edit_distance_levensthein (int) : edit distance compute with Levensthein lib (C extension)

    """
    def __init__(self,
                 source: str,
                 prediction: str,
                 image: str,
                 *args: bool,
                 language='french') -> None:
        """
        Constructs parameters to perform calculations

        Args:
            source (str): reference sequence
            prediction (str) : prediction sequence
            image (str) : path to image
            *args (bool, optional) : activate clean text mode
            language (str) : language use to compute stop words. Defaults on 'french'
        """
        FilesToMetrics.__init__(self, source, prediction, image, *args)
        self.group_to_metrics = FilesToMetrics(source, prediction, image, *args)

        self.source = source
        self.prediction = prediction

        self.distance_matrix_words = self.group_to_metrics.edit_distance_words_matrix
        self.distance_int_char = self.group_to_metrics.edit_distance_char_int
        self.distance_int_word = self.group_to_metrics.edit_distance_word_int

        self.reference_tokens_words = self.group_to_metrics.source_tokens_words
        self.hypothesis_tokens_words = self.group_to_metrics.pred_tokens_words

        self.reference_tokens_char = self.group_to_metrics.source_tokens_char
        self.hypothesis_tokens_char = self.group_to_metrics.pred_tokens_char

        # Pre-processing text data tools for semantic similarity metrics

        self.stop_words = set(stopwords.words(language))

        self.get_sequence_stop = lambda text: \
            [token
             for token in text
             if not token in self.stop_words]

        # SYNTACTIC SIMILARITY METRICS #

        self.edit_distance_levensthein = distance(self.source, self.prediction)


    def _hamming_distance(self):
        """compute the Hamming distance with Levensthein C extension.
        returns Ø if no score => sequences have not the same length
        """
        try:
            edit_hamming_distance = hamming(self.source, self.prediction)
            return edit_hamming_distance
        except:
            return 'Ø'

    def _calculate_wer(self):
        """returns Word Error Rate
        WER = Total Word Errors (Edit distance) / Total Words * 100 (en %)
        """
        result_wer_without_percentage = float((self.distance_int_word)/
                                              len(self.reference_tokens_words))
        #result_wer_without_percentage = float(self.distance_matrix_words[
        # len(self.source_tokens_words)]
        # [len(self.hypothesis_tokens_words)]) / len(self.reference_tokens_words)
        result_wer_without_percentage = truncate(result_wer_without_percentage)
        return result_wer_without_percentage

    def _calculate_wer_percent(self):
        """returns Word Error Rate in percent
        WER * 100
        """
        #result_wer = float(self.distance_matrix_words[
        # len(self.reference_tokens_words)]
        # [len(self.hypothesis_tokens_words)]) / len(self.reference_tokens_words) * 100
        result_wer = float((self.distance_int_word)/
                           len(self.reference_tokens_words)) * 100
        result_wer = truncate(result_wer)
        return result_wer

    def _calculate_word_accuracy(self):
        """returns word accuracy in percent
        Word accuracy = (1 - WER) * 100
        """
        #result_wer = float(self.distance_matrix_words[len(self.reference_tokens_words)]
        # [len(self.hypothesis_tokens_words)]) / len(self.reference_tokens_words)
        result_wer = float((self.distance_int_word) /
                           len(self.reference_tokens_words))
        word_accuracy = 1 - result_wer
        result_word_accuracy = int(word_accuracy * 100)
        return result_word_accuracy

    # see bellow modification in cer too

    def _calculate_cer(self):
        """returns Character Error Rate
        CER = Total Char Errors (Edit distance) / Total Char of
        reference sentence * 100 (en %)
        """
        result_cer_without_percentage = float(self.distance_int_char /
                                              len(self.reference_tokens_char))
        result_cer_without_percentage = truncate(result_cer_without_percentage)
        return result_cer_without_percentage

    def _calculate_cer_percent(self):
        """returns Character Error rate in percent
        CER * 100
        """
        result_cer = float(self.distance_int_char /
                           len(self.reference_tokens_char)) * 100
        result_cer = truncate(result_cer)
        return result_cer

    # SEMANTIC SIMILARITY METRICS #

    # Jaccard index

    def get_jaccard_similarity(self):
        """computes the jaccard index
        J(A,B) = |A ∩ B| / |A u B|

        Preprocess text data
        -------------------
        * use normalize()
        * delete stop words
        """
        sentence_reference = set(self.get_sequence_stop(normalize(self.source)))
        sentence_prediction = set(self.get_sequence_stop(normalize(self.prediction)))
        # compares the words the most words in common
        inter_ref_pred = sentence_reference.intersection(sentence_prediction)
        # return the formula of jaccard index
        return truncate(
            float(
                len(inter_ref_pred)) /
            (
                (len(sentence_reference) + len(sentence_prediction))
                - len(inter_ref_pred)
            )
        )

    # Cosine similarity

    def get_cosine_sim(self):
        """compute cosine similarity
        cosine similarity = (A.B)/(||A||*||B||)

        Info
        ----

        A pure Python implemantation of cosine similarity calculation
        a hack from @TaylorMonacelli (https://stackoverflow.com/questions/
        15173225/calculate-cosine-similarity-given-2-sentence-strings)

        Preprocess text data
        -------------------
        * use normalize()
        * delete stop words

        Details
        -------
        * Transformation of texts into vectors
        * Calculation of cosine similarity
        """

        def text_to_vector(sentence: str) -> object:
            """returns a vectors based on words frequencies
            """
            match_word = re.compile(r'\w+')
            words = match_word.findall(sentence)
            return Counter(words)

        # Preprocess text data
        sentence_reference = " ".join(self.get_sequence_stop
                                      (normalize(self.source)))
        sentence_prediction = " ".join(self.get_sequence_stop
                                       (normalize(self.prediction)))
        # Create vectors
        vector_1 = text_to_vector(sentence_reference)
        vector_2 = text_to_vector(sentence_prediction)

        # Computation
        intersection = set(vector_1.keys()) & set(vector_2.keys())
        numerator = sum([vector_1[x] * vector_2[x] for x in intersection])

        sum1 = sum([vector_1[x] ** 2 for x in vector_1.keys()])
        sum2 = sum([vector_2[x] ** 2 for x in vector_2.keys()])

        # Calculation
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return truncate(float(numerator) / denominator)


class VisualSynTS():
    """A class for plot the syntatic similarity

        Attributes:
            source (str) : reference sentence
            prediction (str) : prediction sentence

            edit_positions (list) : editops returns a list of triples (operation, spos, dpos),
            where operation is one of 'equal', 'replace', 'insert', or 'delete';
            spos and dpos are position of characters in the first (source)
            and the second (destination) strings (Documentation Levenshtein lib).
            Here use it for plot characters pairs of errors.

            # See bellow the documentation of private
            # function get_pair_char_errors_max_occurences()
            pair_char_errors_max_occurences (list)
            total_pair_char_errors_max_occurences (list) : length of
            pair_char_errors_max_occurences

            # See bellow the documentation of
            # private function pairs_characters_errors_confusion_matrix()
            confusion_matrix_pair_char_errors (list)
            letters_normalize (list)

            # See bellow the documentation of
            # private function Ratcliff_Obershelp_steps()
            list_exact (list)
            number_deletions (list)
            number_add (list)

    """
    def __init__(self, source: str, prediction: str) -> None:
        """Parameters to make figure

        Args:
            source (str) : reference sentence
            prediction (str) : prediction sentence
        """

        self.source = source
        self.prediction = prediction
        self.edit_positions = editops(self.source, self.prediction)

        def get_pair_char_errors_max_occurences(reference: str,
                                                hypothesis: str,
                                                edit_positions: list) -> list:
            """create a list of tuples contains :
            * type of transformation (see edittops() doc / replace, insert, delete)
            * char in reference
            * char in prediction
            * number of occurences of this confusion pair

            Example
            -------
            >>> ref = "Oh le beau bateau"
            >>> pred =  "Oh le belle avion"
            >>> edit_pos = editops(ref, pred)
            >>> get_pair_char_errors_max_occurences()
            [(('replace', 'a', 'l'), 1), (('replace', 'u', 'l'), 1),
            (('replace', ' ', 'e'), 1), (('replace', 'b', ' '), 1),
            (('replace', 't', 'v'), 1), (('replace', 'e', 'i'), 1),
            (('replace', 'a', 'o'), 1), (('replace', 'u', 'n'), 1)]

            Args:
                reference (str): reference sentence
                prediction (str): prediction sentence
                edit_positions (list): CF. attribute edit_positions doc

            Returns:
                list : pair of char errors (type, char in reference, char in prediction, occurences)
            """
            list_step = []
            for group in edit_positions:
                for item in group:
                    # we get each modification in the list
                    if item == "replace" or item == "insert" or item == "delete" or item == "equal":
                        list_step.append(item)
                    else:
                        # we replace the position of the characters in the reference
                        # sentence and in the target sentence with the characters
                        # themselves via the index
                        if len(reference) != 0:
                            try:
                                list_step.append(reference[item])
                            except IndexError:
                                break
                        if len(hypothesis) != 0:
                            try:
                                list_step.append(hypothesis[item])
                            except IndexError:
                                break
                        break

            # create a dictionnary with a key as tuples of three items
            # from list_step for retrieve type transformation,
            # char in reference and char in prediction
            # and with value as a number of occurences of this key.
            # After we reshape the dictionnary into a list contaning
            # a tuple that contains tuple of three elements
            # more the number of occurences.
            pair_errors = Counter(list(zip(list_step[::3],
                                           list_step[1::3],
                                           list_step[2::3]))).most_common()

            return pair_errors

        self.pair_char_errors_max_occurences = \
            get_pair_char_errors_max_occurences(self.source,
                                                self.prediction,
                                                self.edit_positions)

        self.total_pair_char_errors_max_occurences = len(self.pair_char_errors_max_occurences)

        def pairs_characters_errors_confusion_matrix(
                pair_char_errors_max_occurences: list) \
                -> tuple:
            """building a confusion matrix of pairs of errors characters between reference sequence
                and prediction sequence. building a list with normalize confusion characters.

                Note
                ----
                We limit confusion matrix with only 10 candidates for better visibility with plot

                Example
                ------
                >>> pair = [(('replace', 'a', 'l'), 1),
                >>>         (('replace', 'u', 'l'), 1),
                >>>         (('replace', ' ', 'e'), 1),
                >>>         (('replace', 'b', ' '), 1)]
                >>> pairs_characters_errors_confusion_matrix(pair)
                ([[0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 1, 0],
                  [1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 1, 0]],
                  ['space', '"a"', '"b"', '"e"', '"l"', '"u"'])

                Args:
                    pair_char_errors_max_occurences (list) : pair of char errors
                    (type, char in reference, char in prediction, occurences)

                Raise:
                    ValueError: if len(pair_char_errors_max_occurences) == 0

                Returns:
                    tuple with :
                    list : confusion matrix of pairs of char, if no confusion 0
                    list : list contains characters with errors, normalize " " in "space"
                """
            try:
                # 10 candidate characters max for the visibility of
                # the matrix including the most frequent error pairs, 0 no confusion
                operations_errors = pair_char_errors_max_occurences[:11] # index for limit
                # building ordered dict for operations errors
                intermediary = defaultdict(Counter)
                for (_, src, tgt), count in operations_errors:
                    intermediary[src][tgt] = count

                letters = sorted(
                    {key for inner in intermediary.values()
                     for key in inner} |
                    set(intermediary.keys()
                        )
                )

                # for space replacement
                letters_normalize = []
                for letter in letters:
                    if letter == " ":
                        letters_normalize.append('space')
                    else:
                        letters_normalize.append(f'"{letter}"')

                confusion_matrix = [[intermediary[src][tgt] for tgt in letters] for src in letters]

                return confusion_matrix, letters_normalize

            # raise error if len(pair_char_errors_max_occurences) == 0
            except ValueError:
                confusion_matrix = []
                letters_normalize = []

                return confusion_matrix, letters_normalize

        self.confusion_matrix_pair_char_errors, \
        self.letters_normalize = pairs_characters_errors_confusion_matrix(
            self.pair_char_errors_max_occurences)

        # attributes for Ratcliff_Obershelp visualizations

        def Ratcliff_Obershelp_steps(source: str, prediction: str) -> list:
            """compute with the Ratcliff / Obershelp algorithm, via difflib,
            a list of characters actually recognized, a list of tuple containing
            the deleted characters and the number of times they have been deleted
            and a list of tuples containing the inserted characters and the number
            of times.

            Example
            ------
            >>> ref = "Ceci n'est pas une pipe"
            >>> pred= "Ceci est un chalumeau"
            >>> list_exact, number_deletions, number_add = Ratcliff_Obershelp_steps(ref, pred)
            >>> list_exact
            ['C', 'e', 'c', 'i', ' ', 'e', 's', 't', ' ', 'u', 'n', 'e']
            >>> number_deletions
            [('p', 3), (' ', 2), ('n', 1), ("'", 1), ('a', 1), ('s', 1), ('i', 1), ('e', 1)]
            >>> number_add
            [('a', 2), ('u', 2), (' ', 1), ('c', 1), ('h', 1), ('l', 1), ('m', 1)]

            Args:
                source (str): reference sequence
                prediction (str) : prediction sequence

            Returns:
                list with:
                    list: list of exact match
                    list: list of tuples deletions and occurences
                    list: list of tuples insertions and occurences
            """
            # creation of a data structure associating
            # the reference sentence and the prediction sentence
            cases = [(source, prediction)]

            # creation of empty lists to recover exactly
            # recognized, deleted and added characters
            list_exact = []
            list_char_delete = []
            list_char_add = []

            for reference, prediction in cases:
                # difflib tokenize the sentence in characters,
                # here we use the intact sequences which not
                # not subjected to cleaning (we keep punctuation, spaces ...)
                for position, char in enumerate(difflib.ndiff(reference, prediction)):
                    # cases common to both sequences
                    if char[0] == ' ':
                        list_exact.append(char[-1])
                    # cases of deletions
                    elif char[0] == '-':
                        list_char_delete.append(char[-1])
                    # cases of insert
                    elif char[0] == '+':
                        list_char_add.append(char[-1])

            number_deletions = Counter(list_char_delete).most_common()
            number_add = Counter(list_char_add).most_common()

            return list_exact, number_deletions, number_add

        self.list_exact, \
        self.number_deletions, \
        self.number_add = Ratcliff_Obershelp_steps(self.source,
                                                   self.prediction)

    def ranking_pairs_characters_errors_html(self):
        """creates a ranking of the most frequently confused pairs of characters for display in HTML

        Note
        ---
        based on get_pair_char_errors_max_occurences()
        """
        error_famous_candidates = self.pair_char_errors_max_occurences
        list_pairs_html = []

        counter = 1
        for a, times in error_famous_candidates:
            if a[0] == "insert" or a[0] == "delete" or a[0] == "replace":
                if a[1] == " ":
                    list_pairs_html.append(f"<p><b>{counter})</b> "
                                           f"TYPE : <b>{a[0]}</b> - "
                                           f"FREQUENCY : <b>{times}</b> times - "
                                           f"DETAILS : <b>space</b> (reference char) "
                                           f"<->  <b>{a[2]}</b> (predicted char)</p><br>")
                    counter += 1
                elif a[2] == " ":
                    list_pairs_html.append(f"<p><b>{counter})</b> "
                                           f"TYPE : <b>{a[0]}</b> - "
                                           f"FREQUENCY : <b>{times}</b> times - "
                                           f"DETAILS : <b>{a[1]}</b> (reference char) "
                                           f"<-> <b>space</b> (predicted char)</p><br>")
                    counter += 1
                else:
                    list_pairs_html.append(f"<p><b>{counter})</b> "
                                           f"TYPE : <b>{a[0]}</b> - "
                                           f"FREQUENCY : <b>{times}</b> times - "
                                           f"DETAILS : <b>{a[1]}</b> (reference char) "
                                           f"<-> <b>{a[2]}</b> (predicted char)</p><br>")
                    counter += 1
            else:
                list_pairs_html.append("<p>no estimation</p><br>")
        return list_pairs_html

    # bound method for Levensthein characters pairs
    # of errors with max occurences in confusion matrix

    def plot_pairs_characters_errors_confusion_matrix(self,
                                                      title="Confusion matrix of reccurent "
                                                            "error characters pairs",
                                                      family='serif',
                                                      color='black',
                                                      weight='normal',
                                                      size=10,
                                                      font_scale=1,
                                                      figsize=(8, 6),
                                                      display_html=True):
        """make a figure with confusion matrix.

        Note
        ----
        based on pairs_characters_errors_confusion_matrix()

        Args:
            title (str) : title of figure.
            Defaults on "Confusion matrix of reccurent error characters pairs"
            family (str) : font family.
            Defaults on 'serif'
            color (str) : font color.
            Defaults on 'black'
            weight (str) : font style.
            Defaults on 'normal'
            size (int) : font size.
            Defaults on 10
            font_scale (int) : font size for values in axis.
            Defaults on 1
            figsize (tuple) : figure size.
            Defaults on (8, 6)
            display_html (bool) : if open on html or in prompt.
            Defaults on True

        Raises:
            ValueError: if len(df_cm) == 0

        """

        try:
            # dataset
            df_cm = pd.DataFrame(self.confusion_matrix_pair_char_errors, self.letters_normalize, self.letters_normalize)

            fig_matrix = plt.figure(figsize=figsize)

            """

            FONT = {'family': family,
                    'color': color,
                    'weight': weight,
                    'size': size,
                    }
                    
            """

            # Generate heatmap
            # for label size
            sn.set(font_scale=font_scale)
            # font size, color of confusion matrix
            ax = sn.heatmap(df_cm, annot=True, annot_kws={"size": size},
                    cmap="nipy_spectral_r")

            # Add title and axis names
            ax.set(ylabel="Reference sentence\n", xlabel="Predicted sentence\n", title=title)

            if display_html:
                return fig_matrix
            else:
                return plt.show()
        except ValueError:
            return "<p>no matrix for test, two sequences are similar</p>"

    # bound method for Ratcliff_Obershelp visualizations

    def plot_hist_ratob_steps(self,
                              title='Sequence to sequence steps',
                              family='serif',
                              color='black',
                              weight='normal',
                              size=13,
                              display_html=True):
        """make an histogram with Ratcliff_Obershelp_steps().
        each bars symbolize exact match, insertions, deletions

        Args:
            title (str) : title of figure.
            Defaults on 'Sequence to sequence steps'
            family (str) : font family.
            Defaults on 'serif'
            color (str) : font color.
            Defaults on 'black'
            weight (str) : font style.
            Defaults on 'normal'
            size (int) : font size.
            Defaults on 10
            display_html (bool) : if open on html or in prompt.
            Defaults on True
        """

        fig_hist, axes = plt.subplots()

        font = {'family': family,
                'color': color,
                'weight': weight,
                'size': size,
                }

        # dataset
        height = [len(self.list_exact), len(self.number_deletions), len(self.number_add)]
        bars = ['Exact Match', 'Deletions', 'Insertions']
        y_pos = np.arange(len(bars))

        # create bars
        ## - width of the bars of the graph
        ## - choose color for each bars
        barwidth = 0.35
        bare = axes.bar(y_pos, height, barwidth, label='differences_sentence', color=['#3CB371', '#D2122E', '#4169E1'])

        # Add title and axis names
        axes.set_title(f'{title}\n')
        axes.set_xlabel('type of steps', fontdict=font)
        axes.set_ylabel('number of characters', fontdict=font)

        # Create names
        axes.set_xticks(y_pos)
        axes.set_xticklabels(bars)

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                axes.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(bare)

        if display_html:
            return fig_hist
        else:
            return plt.show()
