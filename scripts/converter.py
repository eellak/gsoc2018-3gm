#!/usr/bin/env python3

# conversion tool to convert all pdfs in stereo to txt with pdfminer.six
# use with nohup python3 converter.py

import os
import multiprocessing
import ocr
import argparse

MIN_BYTES = 200


def job(x):
    global pdf2txt
    global output_dir
    y = x.replace('.pdf', '.txt')
    y = output_dir + y.split('/')[-1]
    if not os.path.isfile(y):
        os.system('{} {} > {}'.format(pdf2txt, x, y))
        if os.stat(y).st_size <= MIN_BYTES:
            print('File Size unsatisfactory. Performing OCR')
            try:
                ocr.pdfocr2txt(x, y)
            except BaseException:
                print('OCR Failed')

        print('Done')
    else:
        print('already a file')


parser = argparse.ArgumentParser()
parser.add_argument('-pdf2txt', help='pdf2txt.py Executable')
parser.add_argument('-input_dir', help='Input Directory')
parser.add_argument('-output_dir', help='Output Directory')

args = parser.parse_args()

global input_dir
global output_dir
global pdf2txt
input_dir = args.input_dir
output_dir = args.output_dir
pdf2txt = args.pdf2txt

if not output_dir.endswith('/'):
    output_dir = output_dir + '/'

pdfs = []

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.pdf'):
            pdfs.append(os.path.join(root, file))


pool = multiprocessing.Pool(5)
pool.map(job, pdfs)
