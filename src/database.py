'''
    Hosts DB related stuff.
    The database used in this project is MongoDB and it has been chosen
    to provide flexibility with handling large documents with text.
'''

import pprint
import syntax
import copy
from pymongo import MongoClient
from syntax import *

try:
    global client
    client = MongoClient()
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB: %s" % e)



class Database:

    def __init__(self):
        self.db = client['3gmdb']
        self.issues_collection = self.db.issues
        self.laws = self.db.laws

    def insert_issue_to_db(self, issue):
        issue.detect_signatories()
        serializable = {
            'issue_date' : issue.issue_date,
            'issue_number' : issue.issue_number,
            'articles' : issue.articles,
            'extracts' : [(article, list(issues.get_extracts(article))) for article in issue.articles.keys()],
            'non_extracts' : [(article, list(issues.get_non_extracts(article))) for article in issue.articles.keys()],
            'signatories' : [signatory.__dict__ for signatory in issue.signatories]
        }
        seld.issues.insert(serializable)

    def query_from_tree(self, tree):
        if tree['root']['action'] == 'προστίθεται':
            self.laws.insert(tree['law'])
            print('OK')

    def print_laws(self):
        cursor = self.laws.find({})
        for x in cursor:
            pprint.pprint(x)

    def drop_laws(self):
        self.db.drop_collection('laws')
