#!/usr/bin/env python3
# Author: Marios Papachristou
# CLI Tool for codification
# Example Usage: python3 law_codifier.py ../../examples/20180100102.txt initial-out.txt  <../../examples/initial-version.txt > final-version.txt
# Diff versions: diff initial-out.txt final-version.txt

import sys
sys.path.insert(0, '../')
import pparser as parser
import logging
import syntax

# Disable logging due to stdout usage
logger = logging.getLogger()
logger.disabled = True

def codify_pair(source=None, target=None, outfile=None):
    """Codify a pair of issues. Used at the CLI tool
    params: source : Source file. If None then read from stdin
    params: target : Target file. If None then read from stdin
    params: outfile : Output file. If None then output to stdout
    Errors go to stderr
    """
    # Parse issues
    if not source:
        source = sys.argv[1]
    source_issue = parser.IssueParser(source)
    source_issue.detect_new_laws()

    target_issue = parser.IssueParser(None, stdin=True)

    # Detect laws
    target_issue.detect_new_laws()
    source_law = list(source_issue.new_laws.items())[0][1]
    target_law = list(target_issue.new_laws.items())[0][1]

    initial_text = target_law.export_law('issue')
    source_articles = source_law.get_articles_sorted()

    for article in source_articles:
        for paragraph in source_law.get_paragraphs(article):
            try:
                target_law.apply_amendment(paragraph)
            except:
                # If failing write to stderr
                #sys.stderr.write(paragraph)
                pass

    # Write initial version to stdout in pretty format
    with open(sys.argv[2], 'w+') as f:
        f.write(initial_text)

    # Write formatted output to stdout
    sys.stdout.write(target_law.export_law('issue'))

if __name__ == '__main__':
    codify_pair()
