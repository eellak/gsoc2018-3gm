import os 
import sys
from internetarchive import get_item
from converter import list_files
import logging

basename = lambda x: x.split('/')[-1]

uploaded = set([x['identifier'] for x in search_items('collection:greekgovernmentgazette')))

pdfs = list_files(sys.argv[1], '.pdf', recursive=True)

for pdf in pdfs:
	filename = basename(pdf)
	logging.info(pdf) 
	ia_id = 'GreekGovernmentGazette-' + filename
	if ia_id not in uploaded:
		os.system('./ia-upload.sh {}'.format(pdf))
	logging.info('Uploaded ' + filename)
	
