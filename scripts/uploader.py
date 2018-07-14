#!/usr/bin/env python3

import sys
sys.path.insert(0, '../3gm')
from codifier import LawCodifier

def upload(filelist):
    tmp_codifier = LawCodifier()
    for f in filelist:
        tmp_codifier.issues.append(f)

    tmp_codifier.codify_new_laws()
    tmp_codifier.create_law_links()


if __name__ == '__main__':
    upload(sys.argv[1:])
