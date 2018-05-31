import sys
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
		trees = {}
		issue = parser.IssueParser(filename)
		for article in issue.articles.keys():
			for i, extract in enumerate(issue.get_non_extracts(article)):
				trees[i] = syntax.ActionTreeGenerator.generate_action_tree(extract, issue, article)
				for j, t in enumerate(trees[i]):
					try:
						print(j)
						print(t['root'])

						
					except:
						continue
					print('\nPress any key to continue')
					input()

	def add_law(self, filename):
		pass

if __name__ == '__main__':
	codifier = LawCodifier()
	codifier.codify(sys.argv[1])
