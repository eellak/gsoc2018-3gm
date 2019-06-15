"""
Simple Script to run the prodigy server for annotation
Adhering to the GNU GPLv3 Licensing Terms
"""

import argparse
import prodigy


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''This is a simple tool that runs the annotation server for NER datasets.
		For more information visit https://github.com/eellak/gsoc2018-3gm/wiki/''')

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        '-dataset',
        help='Dataset file to store annotations',
        required=True)
    required.add_argument(
        '-input',
        help='Corpus to draw annotations from',
        required=True)
    required.add_argument(
        '-model',
        help='model to train',
        required=True)

    args = parser.parse_args()

    data_set = args.dataset
    input_file = args.input
    model = args.model

    prodigy.serve('ner.manual', data_set, model, input_file)
