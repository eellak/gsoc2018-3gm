#!/usr/bin/env python3

# conversion tool to convert all pdfs in stereo to txt with pdfminer.six
# help: python3 converter --help

import os
import multiprocessing
import ocr
import argparse
import logging

# Minimum bytes for a file to considered purely image
MIN_BYTES = 200

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def job(x):
    global pdf2txt
    global output_dir
    y = x.replace('.pdf', '.txt')
    y = output_dir + y.split('/')[-1]
    if not os.path.isfile(y):
        os.system('{} {} > {}'.format(pdf2txt, x, y))
        if os.stat(y).st_size <= MIN_BYTES:
            logging.info('{}: File Size unsatisfactory. Performing OCR'.format(x))
            ocr.pdfocr2txt(x, y)

        logging.info('{} Done'.format(x))
    else:
        logging.info('{} already a converted file'.format(x))


parser = argparse.ArgumentParser(description='''
    Tool for batch conversion. For more details and documentation visit
    https://github.com/eellak/gsoc2018-3gm/wiki/Document-Processing#using-the-converterpy-tool-for-batch-conversion
''')

required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument('-pdf2txt', help='pdf2txt.py Executable')
required.add_argument('-input_dir', help='Input Directory')
required.add_argument('-output_dir', help='Output Directory')
optional.add_argument(
    '--njobs',
    help='Number of parallel jobs (default = 1)',
    type=int,
    default=1)

args = parser.parse_args()

global input_dir
global output_dir
global pdf2txt
input_dir = args.input_dir
output_dir = args.output_dir
pdf2txt = args.pdf2txt

njobs = args.njobs
if not njobs:
    njobs = 1

if not output_dir.endswith('/'):
    output_dir = output_dir + '/'

pdfs = []

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.pdf'):
            pdfs.append(os.path.join(root, file))

# use multiprocessing for multiple jobs
pool = multiprocessing.Pool(int(njobs))
pool.map(job, pdfs)
