#!/usr/bin/env python3

import sys
sys.path.insert(0, '../') 
import codifier
import argparse

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='''This is the command line tool for codifying documents''')

    optional = argparser.add_argument_group('Optional arguments')

    optional.add_argument(
        '--source',
        help='Source Statute')
    optional.add_argument(
        '--target',
        help='Target Statute'
    )

    optional.add_argument(
        '--output',
        help='Output file'
    )

    args = argparser.parse_args()
    codifier.LawCodifier.codify_pair(args.source, args.target, args.output)
