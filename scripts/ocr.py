#!/usr/bin/env python3
# PDF OCR for Greek Language
# usage: python3 ocr.py infile.pdf outfile.txt

import sys
import pyocr
import pyocr.builders
import io
import logging
import os
import glob
from io import StringIO
from wand.image import Image
from PIL import Image as PI

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def rmdir(d): return os.system('rm -rf ' + d)


def pdfocr2txt(data, outfile, resolution=300):
    tool = pyocr.get_available_tools()[0]
    lang = []

    for l in tool.get_available_languages():
        if l in ['eng', 'ell']:
            lang.append(l)
            break

    if 'ell' not in lang:
        raise Exception(
            'Greek Language not found for Tesseract. Please install it')

    lang = '+'.join(lang)
    req_image = []
    final_text = []
    words = []

    # make temporary directory
    name = data.replace('.pdf', '')
    dir_name = name + '_images'

    try:
        rmdir(dir_name)
        logging.info('Cleaned up old directory')
    except BaseException:
        logging.info('No old directory found')

    os.mkdir(dir_name)
    os.system(
        'convert -density {} -trim -quality 100 -sharpen 0x1.0 {} {}/{}.jpg'.format(
            resolution,
            data,
            dir_name,
            name))
    logging.info('Converted {} to images'.format(data))

    image_filelist = glob.glob(dir_name + '/*.jpg')

    for imgfile in sorted(image_filelist, key=os.path.getmtime):
        img_page = Image(
            filename=imgfile,
            resolution=resolution).make_blob('jpg')
        req_image.append(img_page)

    total = len(req_image)

    for i, img in enumerate(req_image):
        logging.info(
            'Filename: {}. Processing image {} of {}'.format(
                data, i + 1, total))
        txt = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang
        )
        final_text.append(txt)

    logging.info('Writing {} to file'.format(data))

    with open(outfile, 'w+') as f:
        for txt in final_text:
            f.write(txt)

    logging.info('Cleaning {} directory'.format(dir_name))
    rmdir(dir_name)


if __name__ == '__main__':
    pdfocr2txt(sys.argv[1], sys.argv[2])
