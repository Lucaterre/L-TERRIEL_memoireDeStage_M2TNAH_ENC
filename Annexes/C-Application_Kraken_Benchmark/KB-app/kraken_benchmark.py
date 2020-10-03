#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KRAKEN-BENCHMARK CLI PROGRAM

author: Lucas Terriel
contributors / reviewers : Alix Chagué
date : 22/07/2020

-| Summary |-
=============

Main script to launch Kraken-Benchmark.
This script launches a tool in the form of CLI to perform
the transcription of images from the ocr kraken system.
This script also creates objects belonging to STS Tools,
a library to calculate the performance of the transcription model.
Finally, it refers to the function responsible for generating the HTML metrics
dashboard in the form of a Flask application.

-| Usage |-
===========

kraken_benchmark.py [-h] [--input INPUT] [--label] [--verbosity] [--clean_text]

-| Options |-
=============

1. [:input:] Specify location of images, models and ground truth if
not in default location (default = current directory)

2. [:label:] Attach a metadata description on your each set's
image to display it in the HTML dashboard

3. [:verbosity:] View all the objects processed during the automatic transcription phase

4. [:clean-text:] Performs a few cleanning steps to remove
non-alphabetic characters, punctuation, numbers.
depends on the needs of the project.

-| Basic I/O |-

Input => Images / Ground Truth Transcription (.txt files) / model (.mlmodel).
output => kraken benchmark metrics report (.html) with Flask.

# TODO(Lucas) : slice get_transcription more finely to optimize
# TODO(Lucas) : make binarization optional
"""

# built-in packages
import argparse
from copy import deepcopy
import sys
import time
import unicodedata

# external packages
from kraken import rpred, pageseg, binarization
from kraken.lib import models
from PIL import Image
import pyfiglet
from tqdm import tqdm

# local packages
from kb_utils.kb_utils import load_input, get_list_tuple, \
    build_open_files_set, get_metadata, report_log
from STS_Tools.SynSemTS import TranscriptionMetricsTools
from kb_report.routing import generate_html_report


def try_control_step(list_1: list, list_2: list, label_step: str) -> str:
    """perform a test to compare if two lists have the same length

    Examples
    --------

        >>> list_1 = ['a', 'b']
        >>> list_2 = [1, 2, 3]
        >>> label = 'binarization'
        >>> try_control_step(list_1, list_2, label)
        *** Error binarization ***
        TypeError: The number of elements in lists are not the same

    Args:
        list_1 (list): list to compare
        list_2 (list): another list to compare
        label_step (str): label of the current process

    Returns:
        str: success message

    Raises:
        TypeError: if len(list_1) != len(list_2)

    """
    if len(list_1) != len(list_2):
        report_log(f"*** Error {label_step} ***", "E")
        raise TypeError('The number of elements in lists are not the same')
    return report_log(f"\n{'#' * 10} {label_step} done \u2713 {'#' * 10}\n", "S")


def get_transcription(images: list, model: str, opt_verbose: bool) -> list:
    """built from images and an offline recognition model of the text
    of the separate transcripts for each image.
    Process
    -------
    * 1- Open images
    * 2- Binarization
    * 3- Segmentation
    * 4- Text recognition
    * 5- Convert transcription kraken object in string format

    Args:
        images (list): list of user's images
        model (str): relative path to the ML model
        opt_verbose (bool): if user activate verbose option

    Returns:
        list: list contains the text prediction
    """

    # STEP 1 : Loading model
    # Loading the model like kraken.lib.models.TorchSeqRecognizer object
    # --- Issue : find a way to ignore the output precautionary message
    model_load = models.load_any(model)
    # At each new step, a validation message is displayed :
    report_log(f"\n{'#' * 10} Model loaded \u2713 {'#' * 10}\n", "S")

    # STEP 2 : Loading images
    # At each new step we create an empty list to receive the new objects, such as :
    list_image_pil = []
    pbar = tqdm(images)
    for img in pbar:
        pbar.set_description(f'Processing {img} element :')
        # opening images as PIL objects
        try:
            img_pil = Image.open(img)
            list_image_pil.append(deepcopy(img_pil))
        except Exception as exception:
            report_log(f"type : {exception}")
            report_log(f"Error : unable to load images - {img}", "E")
            sys.exit('program exit')


    if opt_verbose:
        report_log(list_image_pil, "V")

    # CONTROL STEP 2
    # At each new step, test if the list created has
    # received the same number of elements as the previous list :
    try_control_step(list_image_pil, pbar, "Images loaded")

    # STEP 3 : Binarization of images
    list_img_binarized = []
    for img_pil in tqdm(list_image_pil, desc='Binarization in progress :'):
        try:
            # creates binarized images
            im_bin = binarization.nlbin(img_pil)
            list_img_binarized.append(deepcopy(im_bin))
        except Exception as exception:
            report_log(f"type : {exception}")
            report_log(f"Error : unable to binarize - {img_pil}", "E")
            sys.exit('program exit')

    if opt_verbose:
        report_log(list_img_binarized, "V")

    # CONTROL STEP 3
    try_control_step(list_img_binarized, list_image_pil, "Binarization")

    # STEP 4 : Segment images
    list_img_seg = []
    for img_bin in tqdm(list_img_binarized, desc='Segmentation in progress :'):
        # retrieves the coordinates of the segments from the binarized image
        try:
            segments_image = pageseg.segment(img_bin, text_direction='horizontal-lr')
            list_img_seg.append(deepcopy(segments_image))
        except Exception as exception:
            report_log(f"type : {exception}")
            report_log(f"Error : unable to segment - {img_bin}", "E")
            sys.exit('program exit')

    if opt_verbose:
        report_log(list_img_seg, "V")

    # CONTROL STEP 4 :
    try_control_step(list_img_seg, list_img_binarized, "Segmentation")

    # create binarized image-segmented image pairs in order to create text recognition
    img_bin_seg = get_list_tuple(list_img_binarized, list_img_seg)

    # STEP 5 : Text recognition
    list_predictions = []
    counter = 0
    while len(img_bin_seg) != len(list_predictions):
        for pair_image_binarized_segments in img_bin_seg:
            for element in pair_image_binarized_segments:
                    # extract from the list binarized image-segmented image the
                    # elements one by one to transform them into an
                    # kraken.rpred.mm_rpred object content the prediction of the text
                    # if the counter is even, get binarized image
                if counter % 2 == 0:
                    binarize_element = element
                    counter += 1
                    # if the counter is odd, get segmented image
                else:
                    segment_element = element
                    # created the text predictions (kraken.rpred.mm_rpred object)
                    output_rpred = rpred.rpred(model_load,
                                               binarize_element,
                                               segment_element,
                                               bidi_reordering=True)
                    list_predictions.append(output_rpred)
                    counter += 1

    if opt_verbose:
        report_log(list_predictions, "V")

    # STEP 6 : Stores kraken predictions in string format like text transcription
    list_transcription = []
    for prediction in tqdm(list_predictions, desc="Transcription in progress :"):
            # create a canvas to accommodate lines of text
            # prediction in string format contained in an image
        canevas = ""
        try:
            for line in prediction:
                # .prediciton is a kraken_ocr_record class attribute for recover the text in
                # kraken.rpred.mm_rpred object
                canevas += f"{unicodedata.normalize('NFC', line.prediction)}"
            list_transcription.append(canevas)
        except Exception as exception:
            report_log(f"Error : unable to transcribe - {prediction}", "E")
            report_log(f"type : {exception}")
            sys.exit('program exit')

    # CONTROL STEP 6
    try_control_step(list_transcription, list_predictions, "Transcription")

    return list_transcription

def main() -> None:
    """launch the cli program.
        Activate the Flask application at the end of the process.
    """

    # ***************************
    # ****** INITIALISATION *****
    # ******    SCRIPT      *****
    # ***************************

    # ----- ASCII edition logo

    ascii_logo_kraken_benchmark = pyfiglet.figlet_format("Kraken Benchmark", font="digital")

    # ----- ARGPARSE OPTIONS FOR THE CLI PROGRAM
    parser = argparse.ArgumentParser(description=
                                     f"Launch the Kraken-Benchmark CLI to "
                                     f"generate a HTML metrics dashboard "
                                     f"in Flask application to evaluate "
                                     f"your transcription models")

    parser.add_argument('--input', '-i',
                        action='store',
                        default='.',
                        help='specify location of images, models and ground truth '
                             'if not in default location (default = current directory)')

    parser.add_argument('--label',
                        '-l',
                        action='store_true',
                        help='attach a label to images')

    parser.add_argument('--verbosity',
                        '-v',
                        action='store_true',
                        help='activate verbosity')

    parser.add_argument('--clean_text',
                        '-c',
                        action='store_true',
                        help='tokenization with clean steps applied : '
                             'replace new line and carriage return with nothing and '
                             'replace the numbers and punctuation with space')


    # ---- Config variables
    # ---- ...generated with Argparse
    args = parser.parse_args()
    opt_verbose = vars(args)['verbosity']  # Print a series of execution messages
    label = vars(args)['label']            # Attach a description to user's images
    clean_text = vars(args)['clean_text']  # Performs few clean steps on text

    # ---- ...others
    if vars(args)['input'] != '.':
        # load_input() needs to be adapted to flexible location of files!
        report_log("Warning : Can't yet deal with files not in default location. "
                   "Input set to current directory.", "W")
        vars(args)['input'] = '.'
    model_name, model, images, group_gt = load_input(vars(args)['input'])

    # ----- Introducing program : 5, 4, 3, 2, 1...take off !
    report_log(f"        \u03A9 WELCOME TO \u03A9 ")
    report_log(ascii_logo_kraken_benchmark)
    if label:
        report_log('* Label mode activate *')
    if clean_text:
        report_log('* Clean text mode activate *')
    time.sleep(5)

    if label:
        metadata = get_metadata(images)
    else:
        metadata = None

    # Build a list contains open & read IO.Wrapper files
    gt_set = build_open_files_set(group_gt)

    # ---- RUN 1 : OCR sequence start
    transcriptions = get_transcription(images, model, opt_verbose)

    # ---- RUN 2 : Grouping ground truth transcription, prediction, and image
    group_gt_model_list = get_list_tuple(gt_set, transcriptions, images)

    # ---- RUN 3 : Metrics Object creation sequence start
    list_statistics = []

    for ground_truth_source, prediction, image in tqdm(group_gt_model_list,
                                                       desc='metrics objects are being created...'):
        # creates objects which allow to give the different
        # metrics for the evaluation of the transcription
        if clean_text:
            list_statistics.append(TranscriptionMetricsTools(ground_truth_source.read(),
                                                             prediction,
                                                             image,
                                                             clean_text)
                                   )
        else:
            list_statistics.append(TranscriptionMetricsTools(ground_truth_source.read(),
                                                             prediction,
                                                             image)
                                   )

    report_log(f"{'#' * 10} Metrics objects created {'#' * 10}\n", "S")

    # ---- RUN 4 : Edit report sequence start
    generate_html_report(metadata, model_name, list_statistics, images)


if __name__ == "__main__":
    # execute only if run as a script
    main()
