#!/usr/bin/env python3
# Batch upload to Internet Archive Script
# usage: batch_ia_upload.py -d /home/repos/GGG/pdf/A --w 3

import os
import sys
from internetarchive import search_items
import logging
import glob
import argparse
import multiprocessing
from converter import list_files


def ia_upload(pdf):
    global pfs
    global uploaded
    filename = basename(pdf, '.pdf')
    print(pdf)
    ia_id = 'GreekGovernmentGazette-' + filename
    if ia_id not in uploaded:
        os.system('./ia-upload.sh {}'.format(pdf))
        print('Uploaded ' + filename)


def basename(x, ext): return x.replace(ext, "").split('/')[-1]


if __name__ == '__main__':
    # argument parser
    argparser = argparse.ArgumentParser(description='''
    Tool for batch upload to Internet Archive for the greekgovernmentgazette collection.
    https://archive.org/details/greekGovernmentgazette''')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    # arguments
    required.add_argument('-d', help='Input directory', required=True)
    optional.add_argument('--w', help='Number of workers', type=int, default=1)

    args = argparser.parse_args()

    # pdfs listed recursively
    pdfs = list_files(args.d, '.pdf', recursive=True)

    # frozenset for faster lookup
    # returns uploaded files
    uploaded = frozenset([x['identifier'] for x in search_items(
        'collection:greekgovernmentgazette')])

    # pool for multiprocessing
    pool = multiprocessing.Pool(args.w)
    pool.map(ia_upload, pdfs)
