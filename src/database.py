'''
    Hosts DB related stuff.
    The database used in this project is MongoDB and it has been chosen
    to provide flexibility with handling large documents with text.
'''

import pprint
from pymongo import MongoClient

try:
    client = MongoClient()
except pymongo.errors.ConnectionFailure, e:
    print "Could not connect to MongoDB: %s" % e


class Database:

    def __init__(self, client):
        self.db = client['3gmdb']
        self.issues_collection = self.db.issues
        self.laws = self.db.laws

    def insert_issue_to_db(self, issue):
        issue.detect_signatories()
        serializable = {
            'issue_date' : issue.issue_date,
            'issue_number' : issue.issue_number,
            'articles' : issue.articles
            'extracts' : dict([(article, list(issues.get_extracts(article))
                            for article in issue.articles.keys()])
            'non_extracts' : dict([(article, list(issues.get_non_extracts(article))
                            for article in issue.articles.keys()])
            'signatories' : [signatory.__dict__ for signatory in issue.signatories]
        }

    def traverse_syntax_tree(self, tree):
        if tree['root']['action'] == 'προστίθεται':
            insertable = {}
            s = ['root']
            while s != []:
                k = s.pop()
                print(k)
                print(tree[k])
                for c in tree['children']:
                    s.append(c)


            self.laws.insert(insertable)
