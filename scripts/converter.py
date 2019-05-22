#!/usr/bin/env python3

# conversion tool to convert all pdfs in stereo to txt with pdfminer.six
# help: python3 converter --help

import os,sys
import multiprocessing
import ocr
import argparse
import logging
import glob

# Minimum bytes for a file to considered purely image
MIN_BYTES = 200

logging.basicConfig(filename="codify_daily.log",filemode = 'a',
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def batch_codify(filelist):
    # batch upload to database / codifier
    sys.path.insert(0, '../3gm')
    import codifier
    import apply_links
    import pparser
    new_laws = {}
    try:
        if (isinstance(filelist,str)):
            filelist = [filelist]
        if not (filelist and isinstance(filelist, list) and all(isinstance(file, str) for file in filelist)):
            raise TypeError('filelist must be a list of one or more strings.')
        
        tmp_codifier = codifier.LawCodifier()
        for f in filelist:
            issue = pparser.IssueParser(filename=f)
            tmp_codifier.issues.append(issue)
            new_laws.update(issue.detect_new_laws())

        tmp_codifier.codify_new_laws()
        tmp_codifier.create_law_links()

        print('Laws added and links created')
        print('Applying links')
        print(new_laws)
        apply_links.apply_all_links(identifiers=None)
    except Exception as e:
        logging.error("Exception occurred while codifying file %s to txt", ''.join(filelist),exc_info=True)

def job(x):
    # document conversion
    global pdf2txt
    global output_dir
    global count
    global upload
    y = x.replace('.pdf', '.txt')
    if output_dir:
        y = output_dir + y.split('/')[-1]
    if not os.path.isfile(y):
        if output_dir:
            os.system('python3 {} {} > {}'.format(pdf2txt, x, y))
        else:
            os.system('python3 {} {}'.format(pdf2txt, x))
        if os.stat(y).st_size <= MIN_BYTES:
            logging.info('{}: File Size unsatisfactory. Performing OCR'.format(x))
            ocr.pdfocr2txt(x, y, resolution=resolution, tmp=tmp)

        logging.info('{} Done'.format(x))
    else:
        logging.info('{} already a converted file'.format(x))

    count.value += 1
    logging.info('Complete {} out of {}'.format(int(count.value), total))

    return y


def list_files(input_dir, suffix, recursive=True):
    # list files (with recursive option in a dir)
    if recursive:
        result = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(suffix):
                    result.append(os.path.join(root, file))
    else:
        result = glob.glob('*{}'.format(suffix))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
        Tool for batch conversion. For more details and documentation visit
        https://github.com/eellak/gsoc2018-3gm/wiki/Document-Processing#using-the-converterpy-tool-for-batch-conversion
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-pdf2txt', help='pdf2txt.py Executable')
    required.add_argument('-input_dir', help='Input Directory')
    optional.add_argument('-output_dir', help='Output Directory (if omitted output goes to stdout)')
    optional.add_argument(
        '--njobs',
        help='Number of parallel jobs (default = 1)',
        type=int,
        default=1)
    optional.add_argument(
        '--tmp',
        help='Temporary files directory (default /var/tmp)',
        default='/var/tmp/')
    optional.add_argument(
        '--resolution',
        help='Resolution of Images in DPI (default 300 dpi)',
        type=int,
        default=300)

    optional.add_argument(
        '--recursive',
        dest='recursive',
        help='Recursive option (default true)',
        action='store_true')

    optional.add_argument(
        '--upload',
        dest='upload',
        help='Upload to database',
        action='store_true')

    args = parser.parse_args()

    global input_dir
    global output_dir
    global pdf2txt
    global tmp
    global resolution
    input_dir = args.input_dir
    output_dir = args.output_dir
    pdf2txt = args.pdf2txt
    tmp = args.tmp
    resolution = args.resolution
    recursive = args.recursive
    upload = args.upload

    njobs = args.njobs

    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'

    pdfs = list_files(input_dir, '.pdf', recursive=recursive)
    txts = list_files(input_dir, '.txt', recursive=recursive)

    global total
    total = len(pdfs)
    global count
    count = multiprocessing.Value('d', 0)

    # use multiprocessing for multiple jobs
    pool = multiprocessing.Pool(int(njobs))
    results = pool.map(job, pdfs)

    # Batch codify results to DB
    batch_codify(results)
