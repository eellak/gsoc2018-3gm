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
import gridfs

try:
    global client
    client = MongoClient()
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB: %s" % e)


class Database:
    """Database Wrapper Class. Serves for database wrapping"""

    def __init__(self):
        """Database wrapper constructor"""
        self.db = client['3gmdb']
        self.issues = self.db.issues
        self.laws = self.db.laws
        self.links = self.db.links
        self.topics = self.db.topics
        self.fs = gridfs.GridFS(self.db)

    def insert_issue_to_db(self, issue):
        """Inserts issue to database"""
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
        """Print laws in the database with pprint"""
        cursor = self.laws.find({})
        for x in cursor:
            pprint.pprint(x)

    def drop_laws(self):
        """Drop laws collection"""
        self.db.drop_collection('laws')

    def drop_issues(self):
        """Drop issues collection"""
        self.db.drop_collection('issues')

    def push_law_to_db(self, law):
        """Push law to database via serializing it
        :params law LawParser object"""
        self.laws.save(law.serialize())

    def query_from_tree(self, law, tree, issue_name=None):
        """Apply query from tree"""
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

    def insert_links(self, links):
        """Insert links to database"""
        for link in links:
            self.links.save(link.serialize())

    def drop_links(self):
        """Drop links collection"""
        self.db.drop_collection('links')

    def drop_topics(self):
        """Drop topics collection"""
        self.db.drop_collection('topics')

    def rollback_laws(self, identifier=None):
        """Rollback laws
        :param identifier If None rollback everything else rollback certain id"""
        if identifier:
            cursor = self.get_json_from_fs(identifier)
        else:
            cursor = self.get_json_from_fs()

        for x in cursor:
            try:
                y = {
                    '_id' : x['_id'],
                    'versions' : [x['versions'][0]]
                }

                self.laws.save(y)
            # Version 0 does not exist
            except IndexError:
                pass

    def rollback_links(self, identifier=None, rollback_laws=False):
        """Rollback links
        :param identifier If none rollback everything else rollback certain id
        :param rollback_laws if true rollback laws
        """
        if identifier:
            cursor = self.links.find({
                '_id' : identifier,
                'actual_links.status' : 'εφαρμοσμένος'
            })
        else:
            cursor = self.links.find({
                'actual_links.status' : 'εφαρμοσμένος'
            })

        for x in cursor:
            tmp = copy.copy(x)
            for y in tmp['actual_links']:
                y['status'] = 'μη εφαρμοσμένος'

            self.links.save(tmp)

        if rollback_laws:
            self.rollback_laws(identifier=identifier)

    def rollback_all():
        """Rollsback everything in the database"""
        self.rollback_links(identifier=None, rollback_laws=True)

    def put_json_to_fs(self, _id, _json):
        dump = json.dumps(_json, ensure_ascii=False).encode('utf-8')
        return self.fs.put(dump, _id=_id)

    def get_json_from_fs(self, _id=None):
        if _id:
            dump = self.fs.find_one({'_id' : _id})
            return json.loads(dump.read().decode('utf-8'))
        else:
            cur = self.fs.find()
            for x in cur:
                yield self.get_json_from_fs(_id=x._id)
            return    
