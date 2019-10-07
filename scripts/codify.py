#!/usr/bin/env python3

# codification tool to codify one pdf file
# help: python3 codify --help
import os
import sys
import ocr
import argparse
import logging
import converter
from pathlib import Path

# Minimum bytes for a file to considered purely image
MIN_BYTES = 200

logging.basicConfig(filename="./logs/codify_daily.log", filemode='a',
                    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def pdf_to_txt(input_pdf, output_txt):
    # document conversion
    try:
        global pdf2txt
        if not os.path.isfile(output_txt):
            if os.path.isfile(input_pdf):
                os.system('python3 {} {} > {}'.format(
                    pdf2txt, input_pdf, output_txt))
            else:
                logging.info('{}: File not found!'.format(input_pdf))
                return False
            if os.stat(output_txt).st_size <= MIN_BYTES:
                logging.info(
                    '{}: File Size unsatisfactory. Performing OCR'.format(input_pdf))
                ocr.pdfocr2txt(input_pdf, output_txt,
                               resolution=resolution, tmp=tmp)

            logging.info('{} Done'.format(input_pdf))
            return True
        else:
            logging.info('{} already a converted file'.format(input_pdf))
            return False
    except Exception as e:
        logging.error(
            "Exception occurred while converting file %s to txt", input_pdf, exc_info=True)
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
        Tool for batch conversion. For more details and documentation visit
        https://github.com/eellak/gsoc2018-3gm/wiki/Document-Processing#using-the-converterpy-tool-for-batch-conversion
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-filename', help='Pdf filename')
    optional.add_argument('--pdf2txt', default='pdf2txt',
                          help='pdf2txt.py Executable')
    optional.add_argument(
        '--tmp',
        help='Temporary files directory (default /var/tmp)',
        default='/var/tmp/')
    optional.add_argument(
        '--resolution',
        help='Resolution of Images in DPI (default 300 dpi)',
        type=int,
        default=300)

    args = parser.parse_args()

    global pdf2txt
    global filename
    global tmp
    global resolution

    pdf2txt = args.pdf2txt
    filename = args.filename
    tmp = args.tmp
    resolution = args.resolution

    data_dir = Path('/home/marios/GGG/GGG/')
    data_dir_pdf = Path(data_dir / 'pdf')
    data_dir_txt = Path(data_dir / 'txt/')

    data_dir_year = filename[:4]
    data_dir_teuxos = filename[4:6].replace("01", "A").replace("02", "B")
    data_dir_subid = filename[6:9]

    input_data_folder = Path(
        data_dir_pdf / data_dir_teuxos / data_dir_year / data_dir_subid)
    output_data_folder = Path(data_dir_txt / data_dir_year)

    full_path_to_pdf = str(input_data_folder / filename)
    full_path_to_txt = str(output_data_folder /
                           filename.replace('.pdf', '.txt'))

    print(full_path_to_pdf)
    res = pdf_to_txt(full_path_to_pdf, full_path_to_txt)
    print(res)
    # codify results to DB
    if (res):
        print('starting codification...')
        converter.batch_codify(full_path_to_txt)
