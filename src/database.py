import pprint
from pymongo import MongoClient
client = MongoClient()
db = client['3gmdb']
ministers_collection = db['ministers']
for minister in actions:
    ministers_collection.insert_one(minister.__dict__)
