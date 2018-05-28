import syntax
import entities
import parser
import database

class UnrecognizedCodificationAction(Exception):

    def __init__(self, extract):
        super().__init__('Unrecognized Codification Action on \n', extract)

class LawCodifier:

    def __init__(self):
        self.laws = {}
        self.issues = {}
        self.db = database.Database()
        self.populate_laws()

    def populate_laws(self):
        cursor = self.db.laws.find({})
        for x in cursor:
            law, identifier = parser.LawParser.from_serialized(x)
            self.laws[identifier] = law

    def codify(self, filename):
        pass

    def add_law(self, filename):
        pass
