#!/usr/bin/env python3

# conversion tool to convert all pdfs in stereo to txt with pdfminer.six
# use with nohup python3 converter.py

import os
import multiprocessing

pdfs = []

for root, dirs, files in os.walk('/home/repos/GGG'):
        for file in files:
                if file.endswith('.pdf'):
                        pdfs.append(os.path.join(root, file))



def job(x):
        y = x.replace('.pdf', '.txt')
        y = './output/' + y.split('/')[-1]
        if not os.path.isfile(y):
                os.system('python3 /home/marios/pdfminer.six/tools/pdf2txt.py {} > {}'.format(x, y))
        else:
                print('already a file')
        print('Done')

pool = multiprocessing.Pool(5)
pool.map(job, pdfs)
