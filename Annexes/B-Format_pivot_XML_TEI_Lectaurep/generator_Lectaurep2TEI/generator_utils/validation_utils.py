#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""RelaxNG Validator module for LTG

author: Lucas Terriel
date : 30/07/2020
"""

import sys

from lxml import etree as ET
from termcolor import colored


def validator_rng(source_xml: str, schema_rng: str):
    """ a little program to validate a xml source
    with a RelaxNG schema and returns differents
    types of logs for validate or unvalidate XML file

    Args:
        source_xml (str) : path to the XML file
        schema_rng (str) : path to the schema
    """

    # STEP 1 : lxml parses the XML and tests if the syntax is valid
    try:
        ET.parse(source_xml)

    except ET.XMLSyntaxError:
        print(colored(f'Failed to Parse XML source, Error Syntax !\n Error log : {sys.exc_info()[1]}', 'red'))
        sys.exit()

    # STEP 2 : If the syntax test is ok, we store the lxml object
    input_xml = ET.parse(source_xml)

    # STEP 3 : lxml parses the RelaxNG schema and creates a RelaxNG object
    relaxng_doc = ET.parse(schema_rng)
    relaxng = ET.RelaxNG(relaxng_doc)

    # STEP 4a : if the RNG test of the xml source returns True, then the document is valid
    if relaxng(input_xml):
        print(colored('Great Job ! Your document is valid !', 'green'))

    # STEP 4b : if the RNG test of the xml source returns False, then the document is invalid
    if not relaxng(input_xml):
        print(colored('Sorry, your document is invalid !', 'red'))
        try:
            relaxng.assertValid(input_xml)
        except ET.DocumentInvalid:
            print(colored(f'Error log : {sys.exc_info()[1]}', 'red'))

        """ Others write like this...
        try:
            relaxng.assert_(input_xml)
        # On renvoie le message d'erreur
        except AssertionError:
            print('Error log : %s' % sys.exc_info()[1])
        """

