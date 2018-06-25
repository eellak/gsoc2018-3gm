import pytest
import parser
import syntax
import entities
import database
import pprint
import helpers
import tokenizer
import re

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

def test_tokenizer():
    # check if tokenizer works correctly
    #
    assert(tokenizer.tokenizer.split('Έλα στις 6 π.μ. και μην αργήσεις. Είναι σημαντικό') == ['Έλα στις 6 π.μ. και μην αργήσεις', ' Είναι σημαντικό'])

def test_syntax_from_string():
    s = '''Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής:  «4.α. Οι υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις και μόνο κατ’ εξαίρεση υπάγονται στη δικαιοδοσία του Μουφτή, εφόσον αμφότερα τα διάδικα μέρη υποβάλουν σχετική αίτησή τους ενώπιόν του για επίλυση της συγκεκριμένης διαφοράς κατά τον Ιερό Μουσουλμανικό Νόμο. Η υπαγωγή της υπόθεσης στη δικαιοδοσία του Μουφτή είναι αμετάκλητη και αποκλείει τη δικαιοδοσία των τακτικών δικαστηρίων για τη συγκεκριμένη διαφορά. Εάν οποιοδήποτε από τα μέρη δεν επιθυμεί την υπαγωγή της υπόθεσής του στη δικαιοδοσία του Μουφτή, δύναται να προσφύγει στα πολιτικά δικαστήρια, κατά τις κοινές ουσιαστικές και δικονομικές διατάξεις, τα οποία σε κάθε περίπτωση έχουν το τεκμήριο της δικαιοδοσίας.  β. Με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί  επιλογής της συγκεκριμένης δικαιοδοσίας, η παράσταση των πληρεξουσίων δικηγόρων, η διαδικασία κατάθεσης και επίδοσής της στο αντίδικο μέρος, η διαδικασία της συζήτησης και της έκδοσης απόφασης, τα θέματα οργάνωσης, σύστασης και διαδικασίας πλήρωσης θέσεων προσωπικού (μονίμων, ιδιωτικού δικαίου αορίστου χρόνου και μετακλητών υπαλλήλων) και λειτουργίας της σχετικής υπηρεσίας της τήρησης αρχείου, καθώς και κάθε σχετικό θέμα για την εφαρμογή του παρόντος. γ. Οι κληρονομικές σχέσεις των μελών της μουσουλμανικής μειονότητας της Θράκης ρυθμίζονται από τις διατάξεις του Αστικού Κώδικα, εκτός εάν ο διαθέτης συντάξει ενώπιον συμβολαιογράφου δήλωση τελευταίας βούλησης, κατά τον τύπο της δημόσιας διαθήκης, με αποκλειστικό περιεχόμενό της τη ρητή επιθυμία του να υπαχθεί η κληρονομική του διαδοχή στον Ιερό Μουσουλμανικό Νόμο. Η δήλωση αυτή είναι ελεύθερα ανακλητή, είτε με μεταγενέστερη αντίθετη δήλωσή του ενώπιον συμβολαιογράφου είτε με σύνταξη μεταγενέστερης διαθήκης, κατά τους όρους του Αστικού Κώδικα. Ταυτόχρονη εφαρμογή του Αστικού Κώδικα και του Ιερού Μουσουλμανικού Νόμου στην κληρονομική περιουσία ή σε ποσοστό ή και σε διακεκριμένα στοιχεία αυτής απαγορεύεται.»'''

    syntax.ActionTreeGenerator.generate_action_tree_from_string(s)

if __name__ == '__main__':
	test_law_parsing_from_government_gazette_issue()
