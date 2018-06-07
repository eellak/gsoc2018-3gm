import sys
import syntax
import entities
import parser
import database


class UnrecognizedCodificationAction(Exception):

	def __init__(self, extract):
		super().__init__('Unrecognized Codification Action on \n', extract)


class LawCodifier:

	def __init__(self, issues_directory=None):
		self.laws = {}
		self.db = database.Database()
		self.populate_laws()
		self.issues = []
		if issues_directory:
			self.populate_issues(issues_directory)

	def populate_laws(self):
		cursor = self.db.laws.find({})
		for x in cursor:
			print(x)
			law, identifier = parser.LawParser.from_serialized(x)
			self.laws[identifier] = law

	def populate_issues(self, directory):
		self.issues = parser.get_issues_from_dataset(directory)

	def codify_issue(self, filename):
		trees = {}
		issue = parser.IssueParser(filename)
		sorted_articles = sorted(issue.articles.keys())

		for article in sorted_articles:

			for i, extract in enumerate(issue.get_non_extracts(article)):
				trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
					extract, issue, article)
				for j, t in enumerate(trees[i]):
					print(t['root'])
					print(t['what'])
					law_id = t['law']['_id']
					print('Law id is ', law_id)

					try:

						if law_id not in self.laws.keys():
							print('Not in keys')
							self.laws[law_id] = parser.LawParser(law_id)

						self.db.query_from_tree(self.laws[law_id], t)

						print('Pushed to Database')
					except Exception as e:
						print(str(e))
						continue

					print('\nPress any key to continue')
					input()

	def codify_law(self, identifier):
		trees = {}

		for issue in self.issues:
			for article in issue.find_statute(identifier):
				print(article, issue.name)
				print('Codifying')

				for i, non_extract in enumerate(issue.get_non_extracts(article)):
					trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
						non_extract, issue, article)
					for j, t in enumerate(trees[i]):
						print(t['root'])
						print(t['what'])
						law_id = t['law']['_id']
						print('Law id is ', law_id)

						try:

							if law_id not in self.laws.keys():
								print('Not in keys')
								self.laws[law_id] = parser.LawParser(law_id)

							self.db.query_from_tree(self.laws[law_id], t)

							print('Pushed to Database')
						except Exception as e:
							print(str(e))
							continue

						print('\nPress any key to continue')
						input()







if __name__ == '__main__':
	codifier = LawCodifier()

	argc = len(sys.argv)

	if argc <= 1:
		print('Please use one or more files as arguments')
		sys.exit(0)

	for i in range(1, argc):
		codifier.codify_issue(sys.argv[i])
