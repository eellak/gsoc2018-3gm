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
            # print(extract)
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
            for t in trees[i]:
                s = ['root']
                while s != []:
                    k = s.pop()
                    print(k)
                    print(t[k])
                    for c in t[k]['children']:
                        s.append(c)

    test_tree = trees[0][0]

    assert( test_tree['root']['action'] == 'προστίθεται' )
    assert( len(test_tree['law']) > 0)
    assert(2 == 2)


if __name__ == '__main__':
    test_action_tree_generator()
