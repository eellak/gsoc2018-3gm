#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
import codifier
import logging

logger = logging.getLogger()
logger.disabled = True

if __name__ == '__main__':

    codifier.LawCodifier.codify_pair()
