import pytest
import parser
import syntax
import database

# Parser Unit Tests

global db
db = database.Database()

# Syntax Tests

def test_action_tree_generator():

    trees = {}
    issue = parser.IssueParser('../data/17.txt')
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            print(extract)
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article, nested=False)
            for t in trees[i]:
                s = ['root']
                while s != []:
                    k = s.pop()
                    print(k)
                    print(t[k])
                    if t[k] == {}: continue
                    for c in t[k]['children']:
                        s.append(c)


    test_tree = trees[0][0]
    print(test_tree['root'])
    db.query_from_tree(test_tree)


    assert( test_tree['root']['action'] == 'προστίθεται' )
    assert( test_tree['law'])
    assert(2 == 2)

def test_action_tree_generator_insert_query(filename='../data/inserter.txt'):
    db.drop_laws()
    trees = {}
    issue = parser.IssueParser(filename)
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
            for t in trees[i]:
                if t['root']['action'] == 'προστίθεται':

                    print('Insertion of')
                    print(t['root'])
                    db.query_from_tree(t)
                    break
    print('Printing Laws Collection')
    db.print_laws()

def test_action_tree_generator_replace_query(filename='../data/replacer.txt'):

    trees = {}
    issue = parser.IssueParser(filename)
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
            for t in trees[i]:
                if t['root']['action'] == 'αντικαθίσταται':

                    print('Replacement of')
                    print(t['root'])
                    db.query_from_tree(t)
                    break
    print('Printing Laws Collection')
    db.print_laws()

def test_action_tree_generator_insert_and_replace():
    db.drop_laws()
    test_action_tree_generator_insert_query()
    test_action_tree_generator_replace_query()


if __name__ == '__main__':
    test_action_tree_generator_insert_and_replace()
