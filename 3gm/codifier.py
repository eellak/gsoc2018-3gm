import sys
import syntax
import entities
import parser
import helpers
import database
import pprint

class UnrecognizedCodificationAction(Exception):
	"""Exception class which is raised when the
	codification action is not well-formed.
	"""

	def __init__(self, extract):
		super().__init__('Unrecognized Codification Action on \n', extract)


class LawCodifier:
	"""This class is responsible for binding the different
	modules of the project into the codifier module.
	Functionality:
	1. Construct the database from Government Gazette issues
	2. Parsing New Laws and Fetching Last Versions from database
	3. Invoke Codification tool that recognizes actions and
	builds queries
	4. Interfacing with MongoDB
	"""

	def __init__(self, issues_directory=None):
		"""Constructor for LawCodifier class
		:param issues_directory : Issues directory
		"""
		self.laws = {}
		self.db = database.Database()
		self.populate_laws()
		self.issues = []
		if issues_directory:
			self.populate_issues(issues_directory)

	def add_directory(issues_directory):
		"""Add additional Directories"""

		self.issues.extend(parser.get_issues_from_dataset(issues_directory))

	def populate_laws(self):
		"""Populate laws from database and fetch latest versions"""

		cursor = self.db.laws.find({"versions":{ "$ne" : None}})
		for x in cursor:

			current_version = 0
			current_instance = None
			for v in x['versions']:
				if int(v['_version']) >= current_version:
					current_version = int(v['_version'])
					current_instance = v


			law, identifier = parser.LawParser.from_serialized(v)
			law.version_index = current_version
			self.laws[identifier] = law

	def populate_issues(self, directory):
		"""Populate issues from directory"""

		self.issues = parser.get_issues_from_dataset(directory)

	def codify_issue(self, filename):
		"""Codify certain issue (legacy)
		:param filename : Issue filename
		"""

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
		"""
		Codify certain law. Search all issues within self.issues

		:param identifier : The law identifier e.g. ν. 1234/5678
		"""
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

							print('Ammendee, ', issue.name)
							self.db.query_from_tree(self.laws[law_id], t, issue.name)

							print('Pushed to Database')
						except Exception as e:
							print(str(e))
							continue

						print('\nPress any key to continue')
						input()

	def codify_new_laws(self):
		"""Append new laws found in self.issues"""

		for issue in self.issues:
			new_laws = issue.detect_new_laws()
			print(new_laws)
			for k in new_laws.keys():
				try:
					serializable = new_laws[k].__dict__()
					serializable['_version'] = 0
					serializable['amendee'] = issue.name
					self.db.laws.save({
						'_id' : new_laws[k].identifier,
						'versions' : [
							serializable
						]
					})
				except:
					pass

	def get_law(self, identifier, export_type='latex'):
		"""Get law string in LaTeX or Markdown string

		:param identifier : Law identifier
		"""
		if export_type not in ['latex', 'markdown']:
			raise Exception('Unrecognized export type')

		if export_type == 'latex':
			cur = self.db.laws.find({'_id' : identifier})
			result = '\chapter*{{ {} }}'.format(identifier)
			for x in cur:
				for y in x['versions']:
					result = result + '\section* {{ Version  {} }} \n'.format(y['_version'])
					for article in sorted(y['articles'].keys(), key=lambda x: int(x)):
						result = result + '\subsection*{{ Άρθρο {} }}\n'.format(article)
						for paragraph in sorted(y['articles'][article].keys()):
							result = result + '\paragraph {{ {}. }} {}\n'.format(paragraph, '. '.join(y['articles'][article][paragraph]))
		elif export_type == 'markdown':
			cur = self.db.laws.find({'_id' : identifier})
			result = '# {}\n'.format(identifier)
			for x in cur:
				for y in x['versions']:
					result = result + '## Version  {} \n'.format(y['_version'])
					for article in sorted(y['articles'].keys(), key=lambda x: int(x)):
						result = result + '### Άρθρο {} \n'.format(article)
						for paragraph in sorted(y['articles'][article].keys()):
							result = result + ' {}. {}\n'.format(paragraph, '. '.join(y['articles'][article][paragraph]))


		return result

	def export_law(self, identifier, outfile, export_type='markdown'):
		if export_type not in ['latex', 'markdown']:
			raise Exception('Unrecognized export type')

		result = self.get_law(identifier, export_type=export_type)
		if export_type == 'latex':
			helpers.texify(result, outfile)
		elif export_type == 'markdown':
			with open(outfile, 'w+') as f:
				f.write(result)

def test():
	cod = LawCodifier('../data/2018')
	cod.codify_new_laws()
	print('Enter a law you wish to texify')
	ans = input()
	cod.export_law(ans, 'foo.md')

codifier = LawCodifier()

if __name__ == '__main__':
	
	argc = len(sys.argv)

	if argc <= 1:
		print('Please use one or more files as arguments')
		sys.exit(0)

	for i in range(1, argc):
		codifier.codify_issue(sys.argv[i])
