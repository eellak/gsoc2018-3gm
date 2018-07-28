#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
import pparser as parser
import logging
import syntax

logger = logging.getLogger()
logger.disabled = True

def codify_pair(source=None, target=None, outfile=None):
    """Codify a pair of issues. Used at the CLI tool
    params: source : Source file. If None then read from stdin
    params: target : Target file. If None then read from stdin
    params: outfile : Output file. If None then output to stdout
    Errors go to stderr
    """
    if not source:
        source = sys.argv[1]
        print(source)
    source_issue = parser.IssueParser(source)
    source_issue.detect_new_laws()
    print('foo')

    target_issue = parser.IssueParser(None, stdin=True)


    target_issue.detect_new_laws()

    source_law = list(source_issue.new_laws.items())[0][1]
    target_law = list(target_issue.new_laws.items())[0][1]

    source_articles = source_law.get_articles_sorted()
    input_txt = target_law.export_law('issue')

    for article in source_articles:
        for paragraph in source_law.get_paragraphs(article):
            try:
                trees = syntax.ActionTreeGenerator.generate_action_tree_from_string(
                    paragraph)

                for t in trees:
                    if t['law']['_id'] == 'ν. 4009/2011':
                        print(t['what']['content'])
            except:
                pass


    # output_txt = target_law.export_law('issue')
    #
    # if outfile:
    #     with open(outfile, 'w+') as f:
    #         f.write(output_txt)
    # else:
    #     sys.stdout.write(output_txt)

if __name__ == '__main__':
    codify_pair()
