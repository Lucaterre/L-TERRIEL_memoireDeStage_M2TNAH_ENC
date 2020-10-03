#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""LECTAUREP TEI GENERATOR CLI

author: Lucas Terriel
date : 30/07/2020

-| Summary |-
============

A program to simulate the generation of an XML TEI pivot format, from :

* image files;
* XML EAD-EAC and;
* XML ALTO.

The TEI template generated at the output responds to the modeling planned for the Lectaurep project.
Please, Refer to the parent ODD.

-| Usage |-
===========

$ main.py [-h] --images IMAGES --ead_eac EAD_EAC --alto ALTO --output
               OUTPUT [--rng RNG]

-| Basic I/O |-
===============

Input => Images / XML EAD EAC / XML ALTO.
Output => XML TEI file generated in output/ directory by default.
"""

import argparse
import time
import sys

from pyfiglet import figlet_format
from termcolor import colored

from generator_utils.validation_utils import validator_rng
from generator_utils.extract_utils import load_input
from generator_utils.build_utils import build_exif_tags, build_catalog_xml, get_parse_and_mix_soup


def main():
    """Start the program with user's
    command line arguments
    """
    # ***************************
    # ****** INITIALISATION *****
    # ******    SCRIPT      *****
    # ***************************

    # ----- ASCII edition logo
    result_logo = figlet_format("Lectaurep TEI Generator", font="digital")

    # ---- ...Constants
    EAD_EAC_COLLECTION = "catalog_ead_eac.xml"
    ALTO_COLLECTION = "catalog_alto.xml"

    XSLT_EADEAC2TEI = "Lectaurep_EADEAC2TEI.xsl"
    XSLT_ALTO2TEI = "Lectaurep_ALTO2TEI.xsl"

    OUTPUT_DIR = './Output/'

    # ----- ARGPARSE OPTIONS FOR THE CLI PROGRAM
    parser = argparse.ArgumentParser(description=
                                     result_logo +
                                     'A program to generate XML-TEI pivot file with XML EAD, '
                                     'EAC-CPF, ALTO and images in input. Based on Lectaurep ODD.')

    parser.add_argument('--images', '-i',
                        required=True,
                        help='path to directory contains images')

    parser.add_argument('--ead_eac', '-e',
                        required=True,
                        help='path to directory contains XML EAD & EAC')

    parser.add_argument('--alto', '-a',
                        required=True,
                        help='path to directory contains XML ALTO')

    parser.add_argument('--output', '-o',
                        required=True,
                        help='name of TEI file output with .xml '
                             'extension placed by default in Output repository')

    parser.add_argument('--rng', '-r',
                        help='relative path for validation test with an RNG scheme')

    args = parser.parse_args()

    rng_schema = args.rng

    # Get files in a list to pass them to other functions from the absolute path

    images = load_input(args.images, '.jpg')
    ead_eac_files = load_input(args.ead_eac, '.xml')
    alto_files = load_input(args.alto, '.xml')

    output = args.output
    output_xmltei = f'{OUTPUT_DIR}{output}'

    # ----- Introducing program :
    print(result_logo)
    time.sleep(2)

    # ----- Control step : the length of the lists containing the XML files cannot be equal to 0
    if len(ead_eac_files) == 0:
        print(colored(f'There are no XML EAD EAC files, please try again '
                      f'or don\'t forget to specify a "/" a the end of path',
                      'red'))
        sys.exit("Program interrupt")
    elif len(alto_files) == 0:
        print(colored(
            f'There are no XML ALTO files, please try again or'
            f' don\'t forget to specify a "/" a the end of path',
            'red'))
        sys.exit("Program interrupt")
    else:
        pass

    # ----- STEP 1 : We build two XML collections (or catalogs) of
    # equivalent XML files to parse them with an XSLT
    build_catalog_xml(ead_eac_files, 'ead_eac')
    build_catalog_xml(alto_files, 'alto')

    # ----- STEP 2 : Saxon parses the XML collections with the corresponding XSL sheet
    # and retrieves the result instantiated as a Beautifulsoup objects to create two kinds of soups
    soup_ead_eac_tei_framework = get_parse_and_mix_soup(EAD_EAC_COLLECTION, XSLT_EADEAC2TEI)
    soup_alto_tei_framework = get_parse_and_mix_soup(ALTO_COLLECTION, XSLT_ALTO2TEI)

    # ---- STEP 3 : Merge of the two soups
    # a) merge facsimile tag (alto) after teiHeader tag in ead_eac TEI framework
    tag_facsimile = soup_alto_tei_framework.find('facsimile')
    tag_teiheader = soup_ead_eac_tei_framework.find('teiHeader')
    tag_teiheader.insert_after(tag_facsimile)

    # b) merge body tag (alto) after text tag in ead_eac TEI Framework
    tag_text = soup_alto_tei_framework.find('text')
    tag_facsimile = soup_ead_eac_tei_framework.find('facsimile')
    tag_facsimile.insert_after(tag_text)

    # ----- STEP 4 : The eac_eac soup becomes the main soup-canvas for the TEI XML pivot
    soup_tei_canevas = soup_ead_eac_tei_framework

    # ----- STEP 5 : Builds <xenoData> XML trees
    # to retrieve EXIF metadata in XML-TEI soup-canvas
    build_exif_tags(images, soup_tei_canevas)

    # ----- STEP 6 : Beautifulsoup formatted tree in Unicode string
    result = soup_tei_canevas.prettify()

    # ----- STEP 7 : Writes XML-TEI pivot format file
    print(colored(f"TEI file generated : {output}", 'green'))
    with open(output_xmltei, 'w') as file_xml_tei:
        file_xml_tei.write(result)

    # ----- STEP 8 (Optional) : RelaxNG validation test
    if rng_schema:
        print("Schema Validation in progress...")
        validator_rng(output_xmltei, rng_schema)


if __name__ == "__main__":
    # execute only if run as a script
    main()
