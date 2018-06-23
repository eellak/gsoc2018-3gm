import pytest
import parser
import syntax
import entities
import database
import pprint
import helpers

global db
db = database.Database()

# Law Parsing Tests


def _test_law_parsing_from_government_gazette_issue():
    issue = parser.IssueParser('../data/15.txt')
    db.issues.save(issue.__dict__())
    new_laws = issue.detect_new_laws()
    for k in new_laws.keys():
        assert(new_laws[k].corpus['15'] == '1.  Η Επιτροπή Κεφαλαιαγοράς χορηγεί άδεια λειτουργίας Α.Ε.Π.Ε.Υ. μόνον εφόσον η αιτούσα εταιρεία έχει επαρκές  αρχικό κεφάλαιο, σύμφωνα με τις απαιτήσεις του Κανονισμού (ΕΕ) 575/2013, λαμβανομένης υπόψη της φύσης της σχετικής επενδυτικής υπηρεσίας ή δραστηριότητας. ')
        db.laws.save(new_laws[k].__dict__())


# Entities Tests

def test_full_numbers_to_integer():
    assert(entities.Numerals.full_number_to_integer(
        'εξακοσιοστό εξηκοστό έκτο') == 666)
    assert(entities.Numerals.full_number_to_integer(
        'τετρακοσιοστός τέταρτος') == 404)

# Syntax Tests


def test_action_tree_generator_insert_query(
        filename='../data/testcases/inserter.txt'):
    trees = {}
    law = parser.LawParser(identifier='ν. 1234/2018')

    issue = parser.IssueParser(filename)
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                extract, issue, article)
            for t in trees[i]:
                if t['root']['action'] == 'προστίθεται':

                    print('Insertion of')
                    print(t['root'])
                    db.query_from_tree(law, t)
                    break
    print('Printing Laws Collection')
    db.print_laws()


def _test_action_tree_generator_delete_query(
        filename='../data/testcases/deleter.txt'):
    trees = {}
    law = parser.LawParser(
        'ν. 1920/1991',
        '../data/24_12_1990_legislative_act.txt')

    issue = parser.IssueParser(filename)
    for article in issue.articles.keys():
        print(article)
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                extract, issue, article)
            for t in trees[i]:
                if t['root']['action'] == 'διαγράφεται':

                    print('Deletition of')
                    print(t['law'])
                    db.query_from_tree(law, t)
                    break
    print('Printing Laws Collection')
    db.print_laws()


def test_action_tree_generator_replace_query(
        filename='../data/testcases/replacer.txt'):
    law = parser.LawParser('ν. 1234/2018')

    trees = {}
    issue = parser.IssueParser(filename)
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                extract, issue, article)
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


def _test_law_parser(
        filename='../data/24_12_1990_legislative_act.txt',
        identifier='ν. 1920/1921'):
    db.drop_laws()
    law = parser.LawParser(identifier, filename)
    # add article
    law.add_article(
        '6',
        '1. Some Example Context. 2. This is the second paragraph. Lorem Ipsum')

    # add paragraph
    law.add_paragraph('6', '3', '3. A paragraph is added here. Enjoy.')
    law.add_article(
        '6',
        '1. Some Example Ammended Context. 2. This is the second paragraph. Lorem Ipsum')

    # replace phrase in entire article
    law.replace_phrase('Example', 'Replaced Example')

    # insert before and after predefined phrase
    law.insert_phrase('before', 'Example', 'Insert before example', '6', '1')
    law.insert_phrase('after', 'Example', 'After', '6', '1')
    law.append_period('Appended period', '6', '1')
    law.insert_period(
        'before',
        'Appended period',
        'Inserted before other period')

    db.laws.save(law.__dict__())

    print('Testing Insertions')
    cursor = db.laws.find({'_id': 'ν. 1920/1921'})
    for x in cursor:
        assert(x['articles']['1']['1'][0] == 'Εντός τριμήνου αφότου κενωθεί θέση Μουφτή, ο κατά τόπο αρμόδιος Νομάρχης, καλεί σε πράξη του τους ενδιαφερόμενους να την καταλάβουν, να υποβάλουν σχετική αίτηση')
        assert(x['articles']['6']['1'][0] == 'Inserted before other period')
        assert(x['articles']['6']['1'][1] ==
               'Some Replaced Insert before example Example After Ammended Context.')
        assert(x['articles']['6']['2'][0] == 'This is the second paragraph')
        assert(x['articles']['6']['2'][1] == 'Lorem Ipsum')
    print('Testing Deletions')

    law.remove_period('Inserted before other period', '6', '1')
    law.remove_phrase('Ipsum', '6', '2')
    db.laws.save(law.__dict__())

    cursor = db.laws.find({'_id': 'ν. 1920/1921'})
    for x in cursor:
        assert(x['articles']['6']['2'][1] == 'Lorem ')

# OBSOLETE
def _test_law_insertion():

    law = parser.LawParser(
        'ν. 1920/1991',
        '../data/24_12_1990_legislative_act.txt')
    flag = False

    trees = {}
    issue = parser.IssueParser('../data/testcases/custom.txt')
    for article in issue.articles.keys():
        for i, extract in enumerate(issue.get_non_extracts(article)):
            trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                extract, issue, article)
            for t in trees[i]:
                if t['root']['action'] == 'προστίθεται':
                    try:
                        print('Insertion of')
                        print(t['root'])
                        db.query_from_tree(law, t)
                    except BaseException:
                        continue

    print('Testing Querying')
    cursor = db.laws.find({'_id': 'ν. 1920/1991'})
    for x in cursor:
        assert(x['versions'][0]['articles']['1']['1'][0] ==
               'Εντός τριμήνου αφότου κενωθεί θέση Μουφτή, ο κατά τόπο αρμόδιος Νομάρχης, καλεί σε πράξη του τους ενδιαφερόμενους να την καταλάβουν, να υποβάλουν σχετική αίτηση')
        assert(x['versions'][0]['articles']['5']['6'][0] == 'Στη νέα παράγραφο έχουμε ότι με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί')


def test_issue_serializer_to_db(filename='../data/17.txt'):
    db.drop_issues()
    issue = parser.IssueParser(filename)
    db.insert_issue_to_db(issue)

# Helpers test
def test_splitting_extracts():
    s = '1. Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής: «4. α. «Οι» υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις» και μόνο κατ’ εξαίρεση υπάγονται'
    e, n = helpers.get_extracts(s)
    assert(e == ['Περί Μουσουλμάνων Θρησκευτικών Λειτουργών', '4. α. «Οι» υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις'])
    assert(n == ['1. Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου ', '» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής: ', '» και μόνο κατ’ εξαίρεση υπάγοντα'])

if __name__ == '__main__':
	test_law_parsing_from_government_gazette_issue()
