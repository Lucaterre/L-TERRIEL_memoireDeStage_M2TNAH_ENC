#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extract tools module for LTG

author: Lucas Terriel
date : 27/05/2020
"""

import glob


def load_input(path: str, extension: str) -> list:
    """retrieve the files path in a list from its absolute path

    Args:
        path (str): path to the file
        extension (str) : file extension ex. .jpg, .xml...

    Return:
        list : list containing files
    """
    path_to_file_list = glob.glob(path + f"*{extension}")
    list_files = [file for file in path_to_file_list]
    return list_files
