#!/usr/bin/env python3
import pytest
import parser
import syntax


# Parser Unit Tests


# Syntax Tests

def test_action_tree_generator():
    trees = {}
    issue = parser.IssueParser('../data/17.txt')
    for article in issue.articles.keys():
        print(issue.articles[article])
        for i, extract in enumerate(issue.get_non_extracts(article)):
            print(extract)
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract)
            print(trees[i])

    test_tree = trees[0][0]

    assert( test_tree['root']['action'] == 'προστίθεται' )
    assert( len(test_tree['where']['legislative_acts']) > 0)
    assert(2 == 2)


if __name__ == '__main__':
    test_action_tree_generator()
