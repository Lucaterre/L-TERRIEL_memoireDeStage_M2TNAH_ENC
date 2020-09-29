#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Building tools module for LTG

author: Lucas Terriel
date : 30/07/2020
"""

from copy import deepcopy
import os

from bs4 import BeautifulSoup as bs
from PIL import Image, ExifTags
from tqdm import tqdm


def build_catalog_xml(files: list, type_file: str) -> None:
    """build XML collection (or catalog) of
    equivalent XML files to parse them with an XSLT
    via the Xpath collection()

    Args:
        files (list) : xml files to be arranged
                    in the xml canvas of the collection
        type_file (str) : type of XML Schema ex. ALTO, EAD...

    """
    catalog_canvas = """
        <collection>
        </collection>
        """
    soup_catalog = bs(catalog_canvas, 'xml')
    root_catalog = soup_catalog.find("collection")
    pbar = tqdm(files, desc=f'Build XML catalog for {type_file} files in progress...')
    for file in pbar:
        doc_tag = soup_catalog.new_tag('doc')
        doc_tag.attrs['href'] = file
        root_catalog.append(deepcopy(doc_tag))
    catalog = soup_catalog.prettify()
    with open(f'catalog_{type_file}.xml', 'w') as f:
        f.write(catalog)


def build_exif_tags(list_images: list, soup_template_TEI: object) -> None:
    """creates TEI Xenodata and Exif fields in XML TEI pivot format for
    EXIF ​​metadata of images

    Args:
        list_images (list): list that contains the
                        images from which to extract metadata
        soup_template_TEI (object): canvas TEI which corresponds to
                        an object instantiated in the class bs4.BeautifulSoup
    """

    # Get the fileDesc tag in the TEI framework
    tag_filedesc = soup_template_TEI.find('fileDesc')

    pbar = tqdm(list_images, desc='Extraction and assembly of EXIF ​​metadata in progress...')

    # Browse the list of images
    for image in pbar:

        # Get the name of the image and not the entire path
        name_image = os.path.basename(image)

        # Get the extension of image
        extension = image.split('.')[-1]

        # Creates xenoData tags for each images
        xenodata_tag = soup_template_TEI.new_tag("xenoData")

        # add the attributes to the new xenoData tag
        xenodata_tag.attrs['xmlns:exif'] = 'http://ns.adobe.com/exif/1.0/'
        xenodata_tag.attrs['facs'] = f"#{name_image.replace(f'.{extension}', '')}"
        xenodata_tag.attrs['n'] = name_image

        # insertion of the xenoData tag after the fileDesc tag
        tag_filedesc.insert_after(xenodata_tag)

        # Get the new xenoData tag in the TEI framework
        tag_xenodata = soup_template_TEI.find('xenoData')

        # Creates exif:Exif tag for each images
        exif_root_tag = soup_template_TEI.new_tag("exif:Exif")

        # Add new exif:Exif tag to xenoData tag
        tag_xenodata.append(deepcopy(exif_root_tag))

        # Get the new exif:Exif tag in the TEI framework
        tag_exif = soup_template_TEI.find('exif:Exif')

        # Opens images with PIL
        image_open = Image.open(image)

        # EXIF metadata recovery
        image_exif = image_open.getexif()

        # If EXIF metadata exists :
        if image_exif:
            # Browse the exif metadata dictionary
            for key, value in image_exif.items():
                if key in ExifTags.TAGS:
                    # Creates exif: tag for each EXIF field contains by images
                    exif_tags = soup_template_TEI.new_tag(f'exif:{str(ExifTags.TAGS[key])}')
                # some values are in bytes
                if type(value) == bytes:
                    """
                     # a little decoder for bytes types in EXIF metadata
                     value_decode = value.decode('utf8')
                     # print(value_decode, "=>", type(value_decode))
                    """
                    # for the moment, we replace the values of type bytes with a message
                    # and not decode
                    exif_tags.append("bytes_values")

                    # adding the EXIF field in the TEI EXIF template
                    tag_exif.append(deepcopy(exif_tags))

                else:
                    # adding the value of EXIF field to exif: tag
                    exif_tags.append(deepcopy(str(value)))

                    # adding the EXIF field in the TEI EXIF template
                    tag_exif.append(deepcopy(exif_tags))
        # Else...Failed
        else:
            pass


def get_parse_and_mix_soup(xml_collection: str, xslt: str) -> object:
    """Parse the XML collection file with the Saxon
    preprocessor from an XSLT stylesheet
    and instantiate the parsing result in
    a Beautifulsoup object

    Args:
        xml_collection (str) : path to XML collection file
        xslt (str) : path to the XSLT stylesheet corresponding
        on the format XML specification

    Return:
        object : soup corresponding to the XML result of the XSLT parsing
    """
    output = os.popen(f"saxon -s:{xml_collection} {xslt}")
    soup = bs(output, 'xml')
    return soup
