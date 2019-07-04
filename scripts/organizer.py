#!/usr/bin/env python3

# Script to organize files in case they
# are all in the same directory
# Usage: ./organizer.py /directory/

import os
import sys
import glob

dir = sys.argv[1]

os.chdir(dir)

files = glob.glob('*.txt')

for f in files:
    x = f[:4]
    if not os.path.isdir(x):
        os.mkdir(x)
    os.rename(f, '{}/{}'.format(x, f))
