'''
    Hosts DB related stuff.
    The database used in this project is MongoDB and it has been chosen
    to provide flexibility with handling large documents with text.
'''

import pprint
from pymongo import MongoClient

client = MongoClient()
db = client['3gmdb']

class DBWrapper:
    pass
