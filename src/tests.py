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
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article, nested=False)
			for t in trees[i]:
				s = ['root']
				while s != []:
					k = s.pop()
					if t[k] == {}: continue
					for c in t[k]['children']:
						s.append(c)


	test_tree = trees[0][0]

	assert(test_tree['root']['action'] == 'προστίθεται')
	assert(test_tree['law'])

def test_action_tree_generator_insert_query(filename='../data/testcases/inserter.txt'):
	trees = {}
	law = parser.LawParser(identifier='ν. 1234/2018')

	issue = parser.IssueParser(filename)
	for article in issue.articles.keys():
		for i, extract in enumerate(issue.get_non_extracts(article)):
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
			for t in trees[i]:
				if t['root']['action'] == 'προστίθεται':

					print('Insertion of')
					print(t['root'])
					db.query_from_tree(law, t)
					break
	print('Printing Laws Collection')
	db.print_laws()

def test_action_tree_generator_delete_query(filename='../data/testcases/deleter.txt'):
	trees = {}
	law = parser.LawParser('ν. 1234/2018')

	issue = parser.IssueParser(filename)
	for article in issue.articles.keys():
		print(article)
		for i, extract in enumerate(issue.get_non_extracts(article)):
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
			for t in trees[i]:
				if t['root']['action'] == 'διαγράφεται':

					print('Deletition of')
					print(t['law'])
					db.query_from_tree(law, t)
					break
	print('Printing Laws Collection')
	db.print_laws()


def test_action_tree_generator_replace_query(filename='../data/testcases/replacer.txt'):
	law = parser.LawParser('ν. 1234/2018')

	trees = {}
	issue = parser.IssueParser(filename)
	for article in issue.articles.keys():
		for i, extract in enumerate(issue.get_non_extracts(article)):
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
			for t in trees[i]:
				if t['root']['action'] == 'αντικαθίσταται':

					print('Replacement of')
					print(t['root'])
					db.query_from_tree(law, t)
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
	law = parser.LawParser(identifier, filename)
	law.add_article('6', '1. Some Example Context. 2. This is the second paragraph. Lorem Ipsum' )
	law.add_paragraph('6', '3', '3. A paragraph is added here. Enjoy.')
	law.add_article('6', '1. Some Example Ammended Context. 2. This is the second paragraph. Lorem Ipsum' )

	db.laws.save(law.__dict__())

	print('Testing Querying')
	cursor = db.laws.find({'_id' : 'ν. 1920/1921'})
	for x in cursor:
		print(x['articles']['1']['1'])
		assert(x['articles']['1']['1'][0] == 'Εντός τριμήνου αφότου κενωθεί θέση Μουφτή, ο κατά τόπο αρμόδιος Νομάρχης, καλεί σε πράξη του τους ενδιαφερόμενους να την καταλάβουν, να υποβάλουν σχετική αίτηση')

def test_law_insertion():
	db.drop_laws()

	law = parser.LawParser('ν. 1920/1991', '../data/24_12_1990_legislative_act.txt')
	flag = False

	trees = {}
	issue = parser.IssueParser('../data/testcases/testcase_1920_1991.txt')
	for article in issue.articles.keys():
		for i, extract in enumerate(issue.get_non_extracts(article)):
			trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
			for t in trees[i]:
				if t['root']['action'] == 'προστίθεται':
					try:
						print('Insertion of')
						print(t['root'])
						db.query_from_tree(law, t)
					except:
						continue


	print('Testing Querying')
	cursor = db.laws.find({'_id' : 'ν. 1920/1991'})
	for x in cursor:
		assert(x['articles']['1']['1'][0] == 'Εντός τριμήνου αφότου κενωθεί θέση Μουφτή, ο κατά τόπο αρμόδιος Νομάρχης, καλεί σε πράξη του τους ενδιαφερόμενους να την καταλάβουν, να υποβάλουν σχετική αίτηση')
		assert(x['articles']['5']['6'][0] == 'Στη νέα παράγραφο έχουμε ότι με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί')
		assert(x['articles']['5']['5'][1] == 'Οι υποθέσεις της παραγράφου 2 ρυθμίζονται από  τις κοινές διατάξεις και μόνο κατ’ εξαίρεση υπάγονται στη δικαιοδοσία του Μουφτή, εφόσον αμφότερα τα διάδικα μέρη υποβάλουν σχετική αίτησή τους ενώπιόν του για επίλυση της συγκεκριμένης διαφοράς κατά τον Ιερό Μουσουλμανικό Νόμο')

def test_issue_serializer_to_db(filename='../data/17.txt'):
	db.drop_issues()
	issue = parser.IssueParser(filename)
	db.insert_issue_to_db(issue)

if __name__ == '__main__':
	test_law_insertion()
	test_action_tree_generator_insert_query()
