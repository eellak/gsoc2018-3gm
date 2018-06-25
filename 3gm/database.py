'''
    Hosts DB related stuff.
    The database used in this project is MongoDB and it has been chosen
    to provide flexibility with handling large documents with text.
'''

import pprint
import syntax
import copy
from pymongo import MongoClient
from bson.objectid import ObjectId
from syntax import *

try:
    global client
    client = MongoClient()
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB: %s" % e)


class Database:

    def __init__(self):
        self.db = client['3gmdb']
        self.issues = self.db.issues
        self.laws = self.db.laws

    def insert_issue_to_db(self, issue):
        issue.detect_signatories()
        serializable = {
            'issue_date': str(
                issue.issue_date),
            'issue_number': issue.issue_number,
            'articles': issue.articles,
            'extracts': [
                (article,
                 list(
                     issue.get_extracts(article))) for article in issue.articles.keys()],
            'non_extracts': [
                (article,
                 list(
                     issue.get_non_extracts(article))) for article in issue.articles.keys()],
            'signatories': [
                signatory.__dict__ for signatory in issue.signatories]}
        self.issues.insert(serializable)

    def print_laws(self):
        cursor = self.laws.find({})
        for x in cursor:
            pprint.pprint(x)

    def drop_laws(self):
        self.db.drop_collection('laws')

    def drop_issues(self):
        self.db.drop_collection('issues')

    def push_law_to_db(self, law):
        self.laws.save(law.serialize())

    def parse_and_push_law(self, identifier, fileneme):
        law = parser.LawParser(filename, identifier)
        self.push_law_to_db(law.__dict__())

    def query_from_tree(self, law, tree, issue_name=None):
        print('Querying from tree')
        result = law.query_from_tree(tree)
        result['_version'] = law.version_index

        if issue_name:
            result['amendee'] = issue_name

        cur = self.laws.find({"_id" : law.identifier, "versions.amendee": { "$ne" : issue_name} } )
        cur = list(cur)
        if cur == []:
            self.laws.save({'_id': law.identifier})
            temp = {'_id' : law.identifier}
        else:
            temp = cur[0]

        if 'versions' in temp.keys():
            temp['versions'].append(result)
        else:
            temp['versions'] = [result]

        print(temp)

        self.laws.save(temp)
