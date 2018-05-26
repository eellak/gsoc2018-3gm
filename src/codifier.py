import syntax
import entities
import parser
import database

class LawCodifier:

    def __init__(self):
        self.laws = {}
        self.issues = {}
        self.db = database.Database()

        
