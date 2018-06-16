#!/usr/bin/env python3
# PDF OCR for Greek Language
# usage: python3 ocr.py infile.pdf outfile.txt

import sys
import pyocr
import pyocr.builders
import io

from io import StringIO
from wand.image import Image
from PIL import Image as PI


def pdfocr2txt(data, outfile):
    tool = pyocr.get_available_tools()[0]
    lang = []

    for l in tool.get_available_languages():
        if l in ['eng', 'grc', 'ell']:
            lang.append(l)
            print('Found ', l)
            break

    if lang == []:
        raise Exception(
            'Greek Language not found for Tesseract. Please install it')

    lang = '+'.join(lang)
    req_image = []
    final_text = []
    words = []

    image_pdf = Image(filename=data, resolution=600)
    image_jpeg = image_pdf.convert('jpeg')
    print('Converted image')

    for img in image_jpeg.sequence:
        img_page = Image(image=img)
        req_image.append(img_page.make_blob('jpeg'))

    total = len(req_image)

    for i, img in enumerate(req_image):
        print('Processing image {} of {}'.format(i + 1, total))
        txt = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang
        )
        final_text.append(txt)

    print('Writing to file')
    with open(outfile, 'w+') as f:
        for txt in final_text:
            f.write(txt)


if __name__ == '__main__':
    pdfocr2txt(sys.argv[1], sys.argv[2])
