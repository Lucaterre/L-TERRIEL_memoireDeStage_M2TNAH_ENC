#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KRAKEN-BENCHMARK UTILS SET

Author : Lucas Terriel
Date : 22/07/2020

set of add-on functions for the kraken-benchmark.py script
"""

# built-in packages
import glob
import os
import shutil

# external packages
from prompt_toolkit.shortcuts import input_dialog
from termcolor import cprint

def load_input(path: str):
    """recover the different user's files in list

        Args:
            path (list): relatif path to access on user's files

        Returns:
            model_name (str) : basename of model
            model_file (str) : path to model
            image_files (list) : list contains user's images
            transcription_gt_files (list) : list contains user's
                                        ground truth files

    """

    model_path = os.path.join(path, os.path.join('*', "*.mlmodel"))
    model_file = glob.glob(model_path, recursive=True)
    model_file = "".join(model_file)
    model_name = os.path.basename(model_file)
    image_path = os.path.join(path, os.path.join('*', "*.jpeg"))
    image_files = sorted(glob.glob(image_path, recursive=True))
    transcription_gt_path = os.path.join(path, os.path.join('*', "*.txt"))
    transcription_gt_files = sorted(glob.glob(transcription_gt_path, recursive=True))
    return model_name, model_file, image_files, transcription_gt_files

def report_log(message, type_log="I") -> None:
    """Print a log report

    Author
    ------
    Alix Chagué

    Details
    -------

    letter code to specify type of report
    ['I' > Info|'W' > Warning|'E' > Error|'S' > Success|'V' > Verbose]

    Args:
        message (str) : message to display
        type_log (str, optional) : type of message. Defaults to "I" (Info)

    """
    if type_log == "I":  # Info
        print(message)
    elif type_log == "W":  # Warning
        cprint(message, "yellow")
    elif type_log == "E":  # Error
        cprint(message, "red")
    elif type_log == "S": # Success
        cprint(message, "green")
    elif type_log == "V":
        cprint(message, "blue")  # Verbose
    else:
        # unknown color parameter, treated as "normal" text
        print(message)


def get_list_tuple(list_1: list, list_2: list, *args: list) -> list:
    """returns sort of list containing tuples made up of elements from two or three lists

        Examples
        --------
            >>> list_1 = ['a', 'b']
            >>> list_2 = [1, 2, 3]
            >>> get_list_tuple(list_1, list_2)
            [('a', 1), ('b', 2)]
            >>> list_1 = ['a', 'b']
            >>> list_2 = [1, 2, 3]
            >>> list_3 = ['name', 'surname']
            >>> get_list_tuple(list_1, list_2, list_3)
            [('a', 1, 'name'), ('b', 2, 'surname')]

        Args:
            list_1 (list): first list to associate
            list_2 (list): second list to associate
            *args (list, optional) : third list to associate

        Returns:
            list: list with tuples contains elements of lists

        """
    if args:
        list_3 = args[0]
        list_tuple = [(list_1[index],
                       list_2[index],
                       list_3[index]) for index in range(min(len(list_1),
                                                             len(list_2),
                                                             len(list_3)))]
    else:
        list_tuple = [(list_1[index],
                       list_2[index]) for index in range(min(len(list_1),
                                                             len(list_2)))]

    return list_tuple


def build_open_files_set(list_files_to_open: list) -> object:
    """build a list of open text files

        Examples
        --------
        >>> list_texts = ['./dataset_GT/GT_1.txt', './dataset_GT/GT_2.txt']
        >>> build_open_files_set(list_texts)
        [<_io.TextIOWrapper name='./dataset_GT/GT_1.txt.txt' mode='r' encoding='UTF-8'>,
        <_io.TextIOWrapper name='./dataset_GT/GT_2.txt.txt' mode='r' encoding='UTF-8'>]

        Args:
            list_files_to_open (list): list of texts file

        Returns:
            object : io.TextIOWrapper
    """
    files_open_set = []
    for text in list_files_to_open:
        file = open(text, "r")
        files_open_set.append(file)

    return files_open_set


def get_metadata(images: list) -> list:
    """open a prompt dialogue if user activate option [label]
    and retrieve all descriptions in a list
    to display on the HTML report

        Args:
            images (list): list of user's images to attach label

        Returns:
            list : list of images'description
    """
    result = []
    for image in images:
        text = input_dialog(
            title='Images metadata',
            text=f'Enter description : {image}').run()
        if text == "":
            result.append('No metadata specify')
        else:
            result.append(text)
    return result


def get_username() -> str:
    """open a prompt dialog : alert and check the username and display it on
    HTML report

    Returns:
        str : stock username to display on HTML report
    """
    username = input_dialog(
        title='Kraken Benchmark',
        text='Please type your name: ').run()
    return username


def arrange_images_in_static(images: list) -> None:
    """manage the static folder with the new user's
    images :
    1) Push images in images folder => static folder
    2) Remove and replace images in static folder
    if user start KB again

    Note
    ----
    Flask load images only from static.

    Args:
        images (list): list of user's images
    """
    # Remove older images from static file
    dir_name = "./kb_report/static"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".jpeg"):
            os.remove(os.path.join(dir_name, item))
        if item.endswith(".jpg"):
            os.remove(os.path.join(dir_name, item))

    # Move new images to static file
    for image in images:
        shutil.copy(image, dir_name)
