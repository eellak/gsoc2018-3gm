#!/usr/bin/env python3
# usage built_pipeline.py laws links topics versions
import os
import sys
pipeline_depth = {
    'laws' : 0,
    'links' : 1,
    'topics' : 2,
    'versions' : 3
}

pipeline = sorted(sys.argv[1:], key = lambda x: pipeline_depth[x])
sys.path.insert(0, './3gm')
import codifier
print('Building codifier')
codifier.build(start=1999, end=2018, data_dir='./data', pipeline=pipeline)
print('Complete')
