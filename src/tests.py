import pytest
import parser
import syntax
import database
import pprint

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

def test_action_tree_generator_delete_query(filename='../data/deleter.txt'):
	db.drop_laws()
	trees = {}
	issue = parser.IssueParser(filename)
	for article in issue.articles.keys():
		print(article)
		for i, extract in enumerate(issue.get_non_extracts(article)):
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
			for t in trees[i]:
				if t['root']['action'] == 'διαγράφεται':

					print('Deletition of')
					print(t['law'])
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

# Parser Unit Tests

def test_law_parser(filename='../data/24_12_1990_legislative_act.txt', identifier='ν. 1920/1921'):
	db.drop_laws()
	test_action_tree_generator_insert_and_replace()
	law = parser.LawParser(filename, identifier)
	db.laws.save(law.__dict__())
	print('Testing Querying')
	cursor = db.laws.find({'_id' : 'ν. 1920/1921'})
	for x in cursor:
		print(x['articles']['1']['1'])
		assert(x['articles']['1']['1'][0] == 'Εντός τριμήνου αφότου κενωθεί θέση Μουφτή, ο κατά τόπο αρμόδιος Νομάρχης, καλεί σε πράξη του τους ενδιαφερόμενους να την καταλάβουν, να υποβάλουν σχετική αίτηση')

def test_issue_serializer_to_db(filename='../data/17.txt'):
	db.drop_issues()
	issue = parser.IssueParser(filename)
	db.insert_issue_to_db(issue)

if __name__ == '__main__':
	test_law_parser()
	test_issue_serializer_to_db()
