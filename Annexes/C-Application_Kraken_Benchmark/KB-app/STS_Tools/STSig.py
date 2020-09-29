#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Lucas Terriel
#
# Sequences to Signals - STSig
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
# Sequences to Signals - STSig is a micro experiemental library as a part of large Sequences to Similarity Tools (STS Tools) mini library
# implemented in Kraken-Benchmark application.
#
# The idea is to produce sequences in the form of visualizable signals, to allow more detailed analyzes of the differences between
# two sequences (substitutions, deletions, inversions, additions).
#
# TODO(Lucas): in progress...

import math
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import pandas as pd


class SetDictionaryCharWeightPosition:
    """Configure the character types, by default the types char are configured
    for the alphabet and the Latin characters in this order :

    alphabetic chars >> chars acute and chars non-acute >> intercaled chars >> numerical chars >> punctuation serie >>
    space serie

    Then, configure the weights of transformations such as accentuation, capitalization, space (fixed value),
    punctuation (fixed value)

    Also see __init__ method and _get_dict_char_weight() boundmethod below.

    Attributes
    ==========

    Basics chars configuration :
    ----------------------------
    ----------------------------

    char_alpha_serie : list
        Alphabetic char serie
    char_num_serie : list
        Numerical char serie
    char_interlacted_serie : list
        Interlacted char serie
    char_punct_serie : list
        punctuation serie
    char_space_serie : list
        space char serie

    Basics chars acute and no acute :
    ---------------------------------
    ---------------------------------

    Note
    ----
    If you choose to configure a series of characters with accent fill
    a list with the same character carrying the accent and another list
    of the same character without accent, Be careful both must be of the same length

    Example
    -------
    alpha_noacute_a = list("aaaaaa") <=> acutes_a = list("áàâäãå")

    Actual list acute
    -----------------
    => a, c, e, i, n, o, u, y

    alpha_noacute_{char in actual list aucute} : list
        Numerical char serie
    alpha_acute_{char in actual list aucute} : list
        Numerical char serie

    Weights of transformations :
    --------------------------------------
    --------------------------------------

    weight_punctuation : int
        weight according to the punctuation add
    weight_acute : int
        weight according to the prominent character
    weight_capitalize : int
        weight according to the capitalize character
    weight_space : int
        weight according to a space

        ****** Defaults values for weight ******

        - weight_punctuation -> 0.5
        - weight_acute -> 0.5
        - weight_capitalize -> 0.1
        - weight_space -> 0

        ****************************************

    """

    def __init__(self) -> None:
        # Set basics chars series
        self.char_alpha_serie = list("abcdefghijklmnopqrstuvwxyz")
        self.num_serie = list("0123456789")
        self.interlacted_serie = list("æœ")
        self.punct_serie = list("][!\"#$%&'()*+,./:;<=>?@\^_`{|}~-—’")
        self.space_serie = list(" ")

        # Set basics chars non-acute series
        self.alpha_noacute_a = list("aaaaaa")
        self.alpha_noacute_c = list("c")
        self.alpha_noacute_e = list("eeee")
        self.alpha_noacute_i = list("iiii")
        self.alpha_noacute_n = list("n")
        self.alpha_noacute_o = list("ooooo")
        self.alpha_noacute_u = list("uuuu")
        self.alpha_noacute_y = list("yy")

        # Set basics chars acute series

        self.acutes_a = list("áàâäãå")
        self.acutes_c = list("ç")
        self.acutes_e = list("éèêë")
        self.acutes_i = list("íìîï")
        self.acutes_n = list("ñ")
        self.acutes_o = list("óòôöõ")
        self.acutes_u = list("úùûü")
        self.acutes_y = list("ýÿ")

        # Set weights transformation

        self.weight_punctuation = 0.5
        self.weight_acute = 0.5
        self.weight_capitalize = 0.5
        self.weight_space = 0

        # list contains all chars (this order is very important, determine the position and char areas
        # for plot signals in next steps - see bellow)

        self.all_char_series = self.char_alpha_serie + self.interlacted_serie + self.num_serie + self.punct_serie + self.space_serie

    def _get_dict_char_weight(self) -> dict:
        """generates a dictionary with the predefined character set
        in __init__method as a key and its weight position in value.

        :return: dictionnary with char (key) and position-weight (value)
        :type return: dict
        """

        def transport_char_alpha_to_weight_cap_acu(acutes_char: list, position: int, weight_acute: int,
                                                   weight_capitalize: int) -> None:
            """main function routine for processing accents in alphabetic char

            :param acutes_char: preset list of acute char
            :type acutes_char: list
            :param position: position of char in dictionnary
            :type position: int
            :param weight_acute: weight for preset emphasis
            :type weight_acute: int
            :weight_capitalize: weight for preset capitalization
            :type weight_capitalize: int
            """
            i = 0
            while i < len(acutes_char):
                for char_acute in acutes_char:
                    position_weight_char[char_acute] = position + weight_acute
                    position_weight_char[char_acute.upper()] = position + weight_acute + weight_capitalize
                    i += 1

        position = 1
        # creation of an empty reference dictionary to accommodate a character and its weight
        position_weight_char = {}
        for char in self.all_char_series:
            # case 1: alphabetic characters (n + 1)
            if char in self.char_alpha_serie:
                position_weight_char[char] = position
                # case 2: uppercase alphabetic characters ((n + 1) +0.1)
                position_weight_char[char.upper()] = position + self.weight_capitalize
                # cases 3 and 4: alphabetic characters with accent ((n + 1) +0.5) and alphabetical characters in capital letters with accent
                # ((n+1)+0.5+0.1)
                if char in self.alpha_noacute_a:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_a, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_c:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_c, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_e:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_e, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_i:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_i, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_n:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_n, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_o:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_o, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_u:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_u, position, self.weight_acute,
                                                           self.weight_capitalize)
                if char in self.alpha_noacute_y:
                    transport_char_alpha_to_weight_cap_acu(self.acutes_y, position, self.weight_acute,
                                                           self.weight_capitalize)
                position += 1
            # case 5: numeric characters (n + 1)
            if char in self.num_serie:
                position_weight_char[char] = position
                position += 1
            # case 6: interlaced characters (n + 1)
            if char in self.interlacted_serie:
                position_weight_char[char] = position
                # case 7: interlaced characters in capital letters ((n + 1) +0.1)
                position_weight_char[char.upper()] = position + self.weight_capitalize
                position += 1
            # case 8: punctuation (0.5)
            if char in self.punct_serie:
                position_weight_char[char] = self.weight_punctuation
            # case 9: space (0)
            if char == " ":
                position_weight_char[char] = self.weight_space
        return position_weight_char


# on créé la fonction pour crypter la sequence signal en dehors de la classe

def encrypt_steps_sentence_to_signal(sequence: str, dictionnary_char_position_weight: dict) -> list:
    """successively encrypts the characters contained in the sequence with
    respect to the key and the dictionary value.
    Also lists the steps in the sequence, such as char1 = 1, char2 = 2 ...

    :param sequence: sequence to encrypt
    :type sequence: str
    :param dictionnary_char_position_weight: dictionnary with char (key) and it weight-position (value)
    :returns: encrypted sequence / steps in the sequence
    :type returns: list
    """

    # case 10 : char no solve in dict (-1)
    encrypt_sequence_weight_position = [dictionnary_char_position_weight[char]
                                        if char in dictionnary_char_position_weight.keys()
                                        else -1
                                        for char in sequence]
    sequence_steps = [char_sequence for char_sequence in range(len(sequence))]

    return encrypt_sequence_weight_position, sequence_steps


def _get_deltas(reference_encrypt: list, prediction_encrypt: list, reference: str, prediction: str) -> int:
    """retrieve the deltas which correspond to the difference in the weight-position
    of sequence 1 compared to sequence 2 such that :

    Formula : delta = yS2 - yS1

    :param reference_encrypt: reference sequence encrypted with dictionary
    :type reference_encrypt: list
    :param prediction_encrypt: prediction sequence encrypted with dictionary
    :type prediction_encrypt: list
    :param reference: sequence of char (reference)
    :type reference: str
    :param prediction: sequence of char (prediction)
    :type prediction: str
    :return: list of deltas
    :type return: list

    """
    deltas = []
    for delta_1, delta_2 in zip(reference_encrypt, prediction_encrypt):
        deltas.append(delta_2 - delta_1)
    return deltas


class SequencesToSignals(SetDictionaryCharWeightPosition):
    """a class to create the dictionary, and retrieve the
    mean of the deltas (located between 0 and 1, if 0 the two
    sequences are similar and if close to 1 the sequences are not really similar)
    and the variance of the deltas (mean squared) to assess the error dispersion
    index (the higher it the higher the distance between the deltas and high).

    Attributes
    ==========
    object_char_position_weight_dict: obj
        get the attributes and properties of the class SetDictionaryCharWeightPosition

    dictionary_latchar_position_weight : dict
        dictionary of the character (key) and its weight-position (value)
        according to the values defined in SetDictionaryCharWeightPosition class

    sequence_reference_encrypt: list
        reference sequence encrypted

    sequence_reference_steps: list
        reference sequence steps

    sequence_prediction_encrypt: list
        prediction sequence encrypted

    sequence_prediction_steps: list
        prediction sequence steps

    Metrics
    =======

    list_deltas: list
        list of deltas (yS2 - yS1) compute with _get_deltas() function
    expected_value_deltas: int
        value of deltas average is the result of (sum(deltas)/total deltas).
        basic it returns a negative result, however for readability
        we multiply the result by the result itself to obtain a positive value between 0 and 1.
    variance_deltas: int
        value of delta variance always positive and all the greater as the values
        of the deltas are spread out. it is a measure of dispersion.
        Formula : sum(deltas**2) - average_deltas ** 2


    Parameters
    ==========
    sequence_reference: str
        user's reference sequence
    sequence_prediction: str
        user's prediction sequence

    """

    def __init__(self, sequence_reference: str, sequence_prediction: str) -> None:
        SetDictionaryCharWeightPosition.__init__(self)
        self.sequence_reference = sequence_reference
        self.sequence_prediction = sequence_prediction
        self.object_char_position_weight_dict = SetDictionaryCharWeightPosition()
        self.dictionary_latchar_position_weight = self.object_char_position_weight_dict._get_dict_char_weight()

        def _get_dictionary_char_pos_weight_to_html(dictionary: dict) -> str:
            datas = {'characters': ['space' if char == ' ' else char for char in dictionary.keys()],
                     'position-weight': [values for values in dictionary.values()]}
            df = pd.DataFrame(data=datas)
            df_html = df.to_html(justify='justify')
            return df_html

        self.dictionary_latchar_position_weight_html = _get_dictionary_char_pos_weight_to_html(self.dictionary_latchar_position_weight)
        self.sequence_reference_encrypt, self.sequence_reference_steps = encrypt_steps_sentence_to_signal(
            self.sequence_reference, self.dictionary_latchar_position_weight)
        self.sequence_prediction_encrypt, self.sequence_prediction_steps = encrypt_steps_sentence_to_signal(
            self.sequence_prediction, self.dictionary_latchar_position_weight)
        self.list_deltas = _get_deltas(self.sequence_reference_encrypt, self.sequence_prediction_encrypt,
                                       self.sequence_reference, self.sequence_prediction)

    def expected_value_deltas(self) -> int:
        """calculates the average of the deltas

        :param list_deltas: list of deltas
        :type list_deltas: list
        :param return: average score of deltas
        :type return: int
        """
        if len(self.sequence_prediction) == 0:
            return "no expected value deltas because your prediction is null"
        else:
            sum_deltas = 0
            for delta in self.list_deltas:
                sum_deltas += delta
                expected_value = (sum_deltas / len(self.list_deltas))
        return expected_value

    def variance_standard_deviation_deltas(self, expected_value: int) -> int:
        """calculates the variance of the deltas

        :param list_deltas: list of deltas
        :type list_deltas: list
        :param returns: variance score of deltas / standard deviation score
        :type return: int
        """
        if len(self.sequence_prediction) == 0:
            return "no variance and standard deviation because the prediction is null"
        else:
            s1 = 0
            n = len(self.list_deltas)
            for delta in self.list_deltas:
                s1 += delta * delta
            variance = (s1 / n) - (expected_value ** 2)
            standard_deviation = math.sqrt(variance)
        return variance, standard_deviation


class PlotSTS(SequencesToSignals):
    """a class to represent the sequences in the form of a signal
    with at x the character steps of the sequences and at y the
    weight positions of the characters.

    Many options are available for visualizations, see below the method
    _plot_sentences_signal() for more details.

    Attributes
    ==========
    reference: str
        user's reference sequence

    prediction: str
        user's prediction sequence

    reference_encrypt: list
        reference sequence encrypted

    reference_steps: list
        reference sequence steps

    prediction_encrypt: list
        prediction sequence encrypted

    prediction_steps: list
        prediction sequence steps

    dictionary_char_weight_cost: dict
        dictionary of the character (key) and its weight-position (value)
        according to the values defined in SetDictionaryCharWeightPosition class

    list_steps_max: list
        retrieves the most longer steps sentence list

    Parameters
    ==========
    reference: str
        user's reference sequence

    prediction: str
        user's prediction sequence

    reference_encrypt: list
        reference sequence encrypted

    reference_steps: list
        reference sequence steps

    prediction_encrypt: list
        prediction sequence encrypted

    prediction_steps: list
        prediction sequence steps

    dictionary_char_weight_cost: dict
        dictionary of the character (key) and its weight-position (value)
        according to the values defined in SetDictionaryCharWeightPosition class

    list_deltas: list
        list of deltas

    """

    def __init__(self,
                 reference,
                 prediction,
                 reference_encrypt,
                 prediction_encrypt,
                 reference_steps,
                 prediction_steps,
                 dictionary_char_weight_cost,
                 list_deltas) -> None:

        SequencesToSignals.__init__(self, reference, prediction)
        self.GroupSequencesToSignals = SequencesToSignals(reference, prediction)

        self.reference = reference
        self.prediction = prediction

        self.reference_encrypt = reference_encrypt
        self.prediction_encrypt = prediction_encrypt

        self.reference_steps = reference_steps
        self.prediction_steps = prediction_steps

        self.dictionary_char_weight_cost = dictionary_char_weight_cost

        self.list_deltas = list_deltas
        self.list_steps_min = min(self.reference_steps, self.prediction_steps)

        # variables for probabilities
        # ---------------------------

        # Average of deltas (μ - mu)
        self.μ = self.GroupSequencesToSignals.expected_value_deltas()

        # Variance and standard deviation (δ - sigma) of deltas
        self.variance, self.δ = self.GroupSequencesToSignals.variance_standard_deviation_deltas(self.μ)

        # initialization of standard deviation intervals

        ## coefficient of intervals

        self.coefficient_large = 2
        self.coefficient_mid = 1.5

        ## by default μ - 2*δ / μ + 2*δ
        self.mu_2δ_negative = (self.μ - self.coefficient_large * self.δ)
        self.mu_2δ_positive = (self.μ + self.coefficient_large * self.δ)

        ## by default μ - 1.5*δ / μ + 1.5*δ
        self.mu_1_5δ_negative = (self.μ - self.coefficient_mid * self.δ)
        self.mu_1_5δ_positive = (self.μ + self.coefficient_mid * self.δ)

        ## by default μ - δ / μ + δ (fixed)
        self.mu_δ_negative = (self.μ - self.δ)
        self.mu_δ_positive = (self.μ + self.δ)

        def catch_sum_deltas_into_intervals(list_deltas: list,
                                            mu_2δ_negative: int,
                                            mu_2δ_positive: int,
                                            mu_1_5δ_negative: int,
                                            mu_1_5δ_positive: int,
                                            mu_δ_negative: int,
                                            mu_δ_positive: int,
                                            mu: int):
            """

            """
            # initialization of the intervals to recover the deltas sums
            sum_deltas_big = 0
            sum_deltas_large = 0
            sum_deltas_mid = 0
            sum_deltas_small = 0

            for delta in list_deltas:
                if (delta <= mu_2δ_negative) or (delta >= mu_2δ_positive):
                    sum_deltas_big += abs(delta)

                elif (mu_1_5δ_positive <= delta < mu_2δ_positive) or (mu_2δ_negative < delta <= mu_1_5δ_negative):
                    sum_deltas_large += abs(delta)

                elif (mu_δ_negative <= delta < mu_1_5δ_negative) or (mu_δ_positive <= delta < mu_1_5δ_positive):
                    sum_deltas_mid += delta

                elif (mu < delta <= mu_δ_positive) or (mu_δ_negative <= delta < mu):
                    sum_deltas_small += delta

            return sum_deltas_small, sum_deltas_mid, sum_deltas_large, sum_deltas_big

        ## retrieving delta sum intervals

        self.sum_deltas_small, \
        self.sum_deltas_mid, \
        self.sum_deltas_large, \
        self.sum_deltas_big = catch_sum_deltas_into_intervals(self.list_deltas,
                                                              self.mu_2δ_negative,
                                                              self.mu_2δ_positive,
                                                              self.mu_1_5δ_negative,
                                                              self.mu_1_5δ_positive,
                                                              self.mu_δ_negative,
                                                              self.mu_δ_positive, self.μ)

    def _plot_sentences_signal(self,
                               dpi=150,
                               save_figure=False,
                               title="Sequences to Signals analyzer\n",
                               sample_b=0,
                               sample_e=70,
                               char_types_area=True,
                               min_number=29,
                               max_number=38,
                               min_alphabetic=1,
                               max_alphabetic=26,
                               min_interlacted=27,
                               max_interlacted=28.5,
                               limit_lines=True,
                               punctuation_line=0.5,
                               space_line=0,
                               unrecognized_char_line=-1,
                               error_boxes=True,
                               average_deltas_scatter=False,
                               display_html=True,
                               figsize=(25, 15)):
        """
        PlotSTS Class method are similar to regular functions.

        Args:

            General Custom Figure
            ---------------------

            dpi: int (by default dpi=150)
                adjusts the quality of the figure
            save_figure: bool (by default save_figure=False)
                The second parameter.
            title: str (by default "Sequences to Signals analyzer")
                figure title

            Determine the length of the sample text
            ---------------------------------------

            sample: int (by default sample=70)
                If you want to get a nice visible figure we
                recommend that you do not exceed 70 char

            Adjust the char spaces
            ----------------------

            Note : adjust the all parameters bellow.

            char_types_area : bool (by default char_types_area=True)
                draw the color limitations spaces on figure

            with :

                min_number/max_number (by default min_number =29/max_number=38)
                min_alphabetic/max_alphabetic (by default min_alphabetic=1/max_alphabetic=26)
                min_interlacted/max_interlacted (by default min_interlacted=27/max_interlacted=28.5)

            Adjust the limit lines
            ----------------------

            Note : adjust the all parameters bellow.

            limit_lines : bool (by default limit_lines=True)
                draw a symbolic lines of special type char

            with :
                punctuation_line (by default punctuation_line=0.5)
                space_line (by default space_line=0)
                unrecognized_char_line (by default unrecognized_char_line=-1)

            Draw Error Boxes
            ----------------

            error_boxes: bool (by default error_boxes=True)
                draw error boxes on the weight-positions of the prediction
                sequence not similar to the reference sequence.

            Draw average deltas scatter
            ---------------------------

            average_deltas_scatter : bool (by default average_deltas_scatter=False)
                draw the mean of the deltas as points.


        Returns:
            plot of sentences into signals

        """

        # Take a text sample if the sentence is more than 70 char (customizable interval)

        if len(self.reference) > sample_e or len(self.prediction) > sample_e:
            reference = self.reference[sample_b:sample_e]
            prediction = self.prediction[sample_b:sample_e]
            reference_steps = self.reference_steps[sample_b:sample_e]
            prediction_steps = self.prediction_steps[sample_b:sample_e]
            reference_encrypt = self.reference_encrypt[sample_b:sample_e]
            prediction_encrypt = self.prediction_encrypt[sample_b:sample_e]
            list_deltas = self.list_deltas[sample_b:sample_e]
            list_step_min = self.list_steps_min[sample_b:sample_e]
        else:
            reference = self.reference
            prediction = self.prediction
            reference_steps = self.reference_steps
            prediction_steps = self.prediction_steps
            reference_encrypt = self.reference_encrypt
            prediction_encrypt = self.prediction_encrypt
            list_deltas = self.list_deltas
            list_step_min = self.list_steps_min

        # initialize the size of the figure and the quality of the resolution
        figure, ax = plt.subplots(dpi=dpi, figsize=figsize)

        # initialize the signals (x: weight / cost of the characters in the sequence /
        # y: sequence of characters)
        plt.plot(reference_steps, reference_encrypt, "-b", label=f'Sequence-signal 1', marker="s", lw=2.5)
        plt.plot(prediction_steps, prediction_encrypt, "-r", label=f'Sequence-signal 2', marker="s", lw=2.5)

        #####################################################################

        # check the average of deltas
        if average_deltas_scatter:
            plt.scatter(list_step_min, list_deltas, s=300, c='coral', label='average of deltas')

        #####################################################################

        # Generate error boxes according to the error position of prediction sequence

        if error_boxes:
            error_boxes = []
            x = []
            y = []
            xerr = []
            yerr = []
            for x_S1, y_S1, x_S2, y_S2 in zip(reference_steps, reference_encrypt, prediction_steps, prediction_encrypt):
                if y_S1 != y_S2:
                    x.append(x_S2)
                    y.append(y_S2)
                    xerr.append(1)
                    yerr.append(1.5)
                    rect = Rectangle((x_S2 - 1, y_S2 - 1.5), 2, 3, color='r', alpha=0.5)
                    error_boxes.append(rect)

            xValues = x
            yValues = y
            xErrorValues = xerr
            yErrorValues = yerr
            plt.scatter(xValues, yValues, zorder=2)
            plt.errorbar(xValues, yValues, xerr=xErrorValues, yerr=yErrorValues,
                         fmt='none', capsize=10, ecolor='k', zorder=1, alpha=1, lw=2)

            collection_errors_boxes = PatchCollection(error_boxes, facecolors='r', alpha=0.3)
            ax.add_collection(collection_errors_boxes)

        #####################################################################

        # Manage character type spaces / Manage area char types

        if char_types_area:
            # number space
            ax.add_artist(patches.Rectangle((0, min_number), (max(len(prediction+reference), len(prediction+reference))), max_number,
                                            edgecolor='black', facecolor='orange',
                                            fill=True, linestyle='dashed', label='rect',
                                            linewidth=3, zorder=1, alpha=0.09))

            # alphabetical letter space
            ax.add_artist(patches.Rectangle((0, min_alphabetic), (max(len(prediction+reference), len(prediction+reference))), max_alphabetic,
                                            edgecolor='black', facecolor='blue',
                                            fill=True, linestyle='dashed', label='rect',
                                            linewidth=3, zorder=1, alpha=0.09))

            # interlaced character space
            ax.add_artist(
                patches.Rectangle((0, min_interlacted), (max(len(prediction+reference), len(prediction+reference))), max_interlacted,
                                  edgecolor='black', facecolor='green',
                                  fill=True, linestyle='dashed', label='rect',
                                  linewidth=3, zorder=1, alpha=0.09))

        #####################################################################

        # Creation of lines to represent the passage of signals by:
        # we define two points (x1, y1) and (x2, y2)
        if limit_lines:
            plt.plot([len(list(range(sample_e))), 0.0], [punctuation_line, punctuation_line], 'm-', lw=3, label='punctuation line')
            plt.plot([len(list(range(sample_e))), 0.0], [space_line, space_line], 'c-', lw=3, label="space line")
            plt.plot([len(list(range(sample_e))), 0.0], [unrecognized_char_line, unrecognized_char_line], 'y-', lw=3,
                     label="unrecognized char line")

        #####################################################################

        # Addition of values in x and y which correspond to the coordinate points
        #ax = plt.gca()
        # -- issue : display the "letter = cost-position" on the ordinate
        # y_labels_axis = []
        # for char, position_cost in self.dictionary_char_weight_cost.items():
        # if position_cost in self.prediction_deltas or position_cost in self.reference_deltas:
        # y_labels_axis.append(f'{char}={position_cost}')
        # ax.yaxis.set_ticklabels(set(y_labels_axis))
        #ax.xaxis.set_ticks(list(range(sample_b, sample_e)))

        ax.set_xlim(sample_b, sample_e)
        ax.xaxis.set_ticks(list(range(sample_b, sample_e)))
        ax.yaxis.set_ticks(reference_encrypt + prediction_encrypt)
        #ax.yaxis.set_tick_params(labelsize=8)
        #ax.xaxis.set_tick_params(labelsize=8)
        #ax.yaxis.grid(True)
        #ax.xaxis.grid(True)
        plt.xticks(rotation=65)
        plt.yticks(rotation=13)
        #plt.xscale("linear")

        #####################################################################

        # Section to customize the visualizations

        # highlights the abscess and ordinate axis
        plt.axhline(color='k')  # axe des x
        plt.axvline(color='k')  # axe des y

        plt.suptitle(title, family='serif', fontsize=26, ha='center')  # print general title
        plt.grid(color='k', linestyle='-', linewidth=0.4)  # print a grid
        plt.xlabel('position of char in reference sentence and prediction sentence', family='serif', fontsize=14)  # x label
        plt.ylabel('weight-position per char in dictionary', family='serif', fontsize=14)  # y label
        plt.legend()  # print labels

        #####################################################################

        # If save figure activate
        if save_figure:
            plt.savefig(f"{title}.png", dpi=dpi)

        if display_html:
            return figure
        else:
            return plt.show()

    """
    
    => consider this method when the flask route is operational
    
    def _plot_probabilities(self,
                            save_figure=False,
                            dpi=150,
                            title="Deltas Vizualisation",
                            display_html=True,
                            figsize=(25, 15)):

        figure, ax = plt.subplots(figsize=figsize, dpi=dpi)
        plt.plot(self.list_steps_min, self.list_deltas, "-k", label=f'deltas S1-S2', marker="s", lw=1)
        plt.plot([len(self.list_steps_min), 0.0], [self.μ, self.μ], 'm-', lw=3, label='average deltas')

        # Design percent

        # plt.text([len(self.list_steps_min), 0.0],[self.mu_2δ_positive, self.mu_2δ_positive],
        # f"{(sum_delta_2δ/len(list_deltas))*100} %",
        # horizontalalignment='center',
        # verticalalignment='center',
        # transform = ax.transAxes)

        # Draw intervals with lines

        plt.plot([len(self.list_steps_min), 0.0], [self.mu_2δ_positive, self.mu_2δ_positive], 'g--', lw=3,
                 label='average deltas + 2δ')
        plt.plot([len(self.list_steps_min), 0.0], [self.mu_2δ_negative, self.mu_2δ_negative], 'g--', lw=3,
                 label='average deltas - 2δ')
        plt.plot([len(self.list_steps_min), 0.0], [self.mu_1_5δ_positive, self.mu_1_5δ_positive], 'r--', lw=3,
                 label='average deltas + 1.5δ')
        plt.plot([len(self.list_steps_min), 0.0], [self.mu_1_5δ_negative, self.mu_1_5δ_negative], 'r--', lw=3,
                 label='average deltas - 1.5δ')
        plt.plot([len(self.list_steps_min), 0.0], [self.mu_δ_positive, self.mu_δ_positive], 'c--', lw=3,
                 label='average deltas + δ')
        plt.plot([len(self.list_steps_min), 0.0], [self.mu_δ_negative, self.mu_δ_negative], 'c--', lw=3,
                 label='average deltas - δ')

        # Section to customize the visualizations

        # highlights the abscess and ordinate axis
        plt.axhline(color='k')  # axe des x
        plt.axvline(color='k')  # axe des y

        plt.suptitle(title, family='monospace', fontsize=25, ha='center')  # print general title
        plt.grid(color='k', linestyle='-', linewidth=0.4)  # print a grid
        plt.xlabel('SEQUENCES', family='serif', fontsize=14)  # x label
        plt.ylabel('DELTAS', family='serif', fontsize=14)  # y label
        plt.legend()  # print labels

        if save_figure:
            plt.savefig(f"{title}.png", dpi=dpi)

        if display_html:
            return figure
        else:
            return plt.show()

    def _report_probabilities(self):
        print(f"1) delta <= -2δ ou delta >= 2δ : {truncate((sum_delta_2δ/len(list_deltas)) * 100)} %")
        print(f"2) -1.5δ <= delta < -2δ ou 1.5δ <= delta < 2δ: {truncate((sum_delta_1_5δ/len(list_deltas)) * 100)} %")
        print(f"3) δ <= delta < -1.5δ ou δ <= delta < 1.5δ: {truncate((sum_1_5δ_δ/len(list_deltas)) * 100)} %")
        print(f"4) avg < delta <= δ ou -δ <= delta < avg  : {truncate((sum_delta_δ/len(list_deltas)) * 100)} %")"""
