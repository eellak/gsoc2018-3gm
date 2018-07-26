import os 
import sys
from internetarchive import search_items
import logging
import glob
import multiprocessing

def list_files(input_dir, suffix, recursive=True):
    if recursive:
        result = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(suffix):
                    result.append(os.path.join(root, file))
    else:
        result = glob.glob('*{}'.format(suffix))
    return result

def ia_upload(pdf):
        global pfs
        global uploaded
        filename = basename(pdf, '.pdf')
        logging.info(pdf)
        ia_id = 'GreekGovernmentGazette-' + filename
        if ia_id not in uploaded:
                os.system('./ia-upload.sh {}'.format(pdf))
        logging.info('Uploaded ' + filename)

basename = lambda x, ext: x.replace(ext,"").split('/')[-1]

# frozenset for O(logn) lookup
uploaded = frozenset([x['identifier'] for x in search_items('collection:greekgovernmentgazette')])

pdfs = list_files(sys.argv[1], '.pdf', recursive=True)

try:
	workers = int(sys.argv[2])
except:
	workers = 1

# pool for multiprocessing
pool = multiprocessing.Pool(workers)
pool.map(ia_upload, pdfs)
