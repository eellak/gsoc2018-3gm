#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import multiprocessing
import numpy as np
from datetime import date, datetime, time
from entities import *
from helpers import *
from syntax import *
import os
import gensim
import pprint
from gensim.models import KeyedVectors
import logging
logging.basicConfig(
	format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import itertools
import glob
params = {'size': 200, 'iter': 20,  'window': 2, 'min_count': 15,
		  'workers': max(1, multiprocessing.cpu_count() - 1), 'sample': 1E-3, }

date_regex = re.compile('(\
([1-9]|0[1-9]|[12][0-9]|3[01])\
[-/.\s+]\
(1[1-2]|0[1-9]|[1-9]|Ιανουαρίου|Φεβρουαρίου|Μαρτίου|Απριλίου|Μαΐου|Ιουνίου|Ιουλίου|Αυγούστου|Νοεμβρίου|Δεκεμβρίου|Σεπτεμβρίου|Οκτωβρίου|Ιαν|Φεβ|Μαρ|Απρ|Μαϊ|Ιουν|Ιουλ|Αυγ|Σεπτ|Οκτ|Νοε|Δεκ)\
(?:[-/.\s+](1[0-9]\d\d|20[0-9][0-8]))?)')

class IssueParser:
	"""
		This is a class for holding information about an issue in
		computer-friendly form. It is responsible for:
		1. Detecting Dates
		2. Split document to articles
		3. Split articles to extracts and non-extracts for assisting
		in construction of the parse tree for each ROI.
		4. Detect Signatories of Given Documents
		5. Train a word2vec model with gensim for further usage."""

	def __init__(self, filename, toTxt=False):
		self.filename = filename
		self.lines = []
		tmp_lines = []
		with open(filename, 'r') as infile:
			# remove ugly hyphenthation
			while 1 == 1:
				l = infile.readline()
				if not l:
					break
				l = l.replace('-\n', '')
				l = l.replace('\n', ' ')
				tmp_lines.append(l)


		for line in tmp_lines:
			if line == '':
				continue
			elif line.startswith('Τεύχος') or line.startswith('ΕΦΗΜΕΡΙ∆Α TΗΣ ΚΥΒΕΡΝΗΣΕΩΣ'):
				continue
			else:
				try:
					n = int(line)
					continue
				except ValueError:
					self.lines.append(line)
					if line.startswith('Αρ. Φύλλου'):
						self.issue_number = int(line.split(' ')[-2])

		self.dates = []
		self.find_dates()
		self.articles = {}
		self.sentences = {}
		self.find_articles()

	def find_dates(self):
		"""Detect all dates withing the given document"""

		for i, line in enumerate(self.lines):
			result = date_regex.findall(line)
			if result != []:
				self.dates.append((i, result))

		if self.dates == []:
			raise Exception('Could not find dates!')

		self.issue_date = string_to_date(self.dates[0][1][0])
		self.signed_date = self.dates[-1]

		return self.dates

	def find_articles(self, min_extract_chars=100):
		"""Split the document into articles,
		Detect Extracts that are more than min_extract_chars.
		Extracts start with quotation marks	(«, »).
		Strip punctuation and split document into sentences.
		"""

		article_indices = []
		for i, line in enumerate(self.lines):
			if line.startswith('Άρθρο') or line.startswith('Ο Πρόεδρος της Δημοκρατίας'):
				article_indices.append((i, line))
				self.articles[line] = ''

		for j in range(len(article_indices) - 1):
			self.articles[article_indices[j][1]] = ''.join(
				self.lines[article_indices[j][0] + 1:  article_indices[j+1][0]])

		try:
			del self.articles['Ο Πρόεδρος της Δημοκρατίας']
		except:
			pass

		self.extracts = {}
		self.non_extracts = {}

		for article in self.articles.keys():
			# find extracts
			left_quot = [m.start()
						 for m in re.finditer('«', self.articles[article])]
			right_quot = [m.start()
						  for m in re.finditer('»', self.articles[article])]
			left_quot.extend(right_quot)
			temp_extr = sorted(left_quot)
			res_extr = []
			c = '«'
			for idx in temp_extr:
				if c == '«' and self.articles[article][idx] == c:
					res_extr.append(idx)
					c = '»'
				elif c == '»' and self.articles[article][idx] == c:
					res_extr.append(idx)
					c = '«'
			self.extracts[article] = list(zip(res_extr[::2], res_extr[1::2]))

			# drop extracts with small chars
			self.extracts[article] = sorted(list(
				filter(lambda x: x[1] - x[0] + 1 >= min_extract_chars, self.extracts[article])), key=lambda x: x[0])

			tmp = self.articles[article].strip('-').split('.')

			# remove punctuation
			tmp = [re.sub(r'[^\w\s]', '', s) for s in tmp]
			tmp = [line.split(' ') for line in tmp]
			self.sentences[article] = tmp

	def get_extracts(self, article):
		"""Get direct parts that should be added, modified or deleted"""
		for i, j in self.extracts[article]:
			yield self.articles[article][i + 1: j]

	def get_non_extracts(self, article):
		"""Get non-extracts i.e. where the commands for ammendments
		can be found"""

		if len(self.extracts[article]) == 0:
			return
		x0, y0 = self.extracts[article][0]
		yield self.articles[article][0: max(0, x0)]

		for i in range(1,  len(self.extracts[article]) - 1):
			x1, y1 = self.extracts[article][i]
			x2, y2 = self.extracts[article][i+1]
			yield self.articles[article][y1 + 1: x2]
		xl, yl = self.extracts[article][-1]

		yield self.articles[article][yl + 1:]

	def get_alternating(self, article):
		"""Get extracts and non-extracts alternating as a generator"""

		# start with an extract
		if self.extracts[article][0] == 0:
			flag = False
		else:
			flag = True

		extracts_ = list(self.get_extracts(article))
		non_extracts_ = list(self.get_non_extracts(article))

		for e, n in itertools.zip_longest(extracts_, non_extracts_):
			if flag:
				if n != None:
					yield n
				if e != None:
					yield e
			else:
				if e != None:
					yield e
				if n != None:
					yield n

	def all_sentences(self):
		for article in self.sentences.keys():
			for sentence in self.sentences[article]:
				yield sentence

	def detect_signatories(self):
		self.signatories = set([])
		for i, line in enumerate(self.lines):
			if line.startswith('Ο Πρόεδρος της Δημοκρατίας'):
				minister_section = self.lines[i:]
				break

		for i, line in enumerate(minister_section):
			for minister in ministers:
				x = minister.is_mentioned(line)
				if x != None:
					self.signatories |= set([minister])

		for signatory in self.signatories:
			print(signatory)

		self.signatories = list(self.signatories)

		return self.signatories

	def train_word2vec(self):

		self.all_sentences = [sentence for sentence in self.all_sentences()]

		self.model = gensim.models.Word2Vec(self.all_sentences, **params)
		print('Model train complete!')
		self.model.wv.save_word2vec_format('model')


def generate_model_from_government_gazette_issues(directory='../data'):
	cwd = os.getcwd()
	os.chdir(directory)
	filelist = glob.glob('*.pdf'.format(directory))
	issues = []
	all_sentences = []
	for filename in filelist:
		outfile = filename.strip('.pdf') + '.txt'
		if not os.path.isfile(outfile):
			os.system('pdf2txt.py {} > {}'.format(filename, outfile))
		issue = IssueParser(outfile)
		all_sentences.extend(issue.all_sentences())
		issues.append(issue)
	model = gensim.models.Word2Vec(all_sentences, **params)

	os.chdir(cwd)
	return issues, model

def generate_model_from_government_gazette_issues(directory='../data'):
	cwd = os.getcwd()
	os.chdir(directory)
	filelist = glob.glob('*.pdf'.format(directory))
	issues = []
	for filename in filelist:
		outfile = filename.strip('.pdf') + '.txt'
		if not os.path.isfile(outfile):
			os.system('pdf2txt.py {} > {}'.format(filename, outfile))
		issue = IssueParser(outfile)
		issues.append(issue)

	os.chdir(cwd)
	return issues, model

def train_word2vec_on_test_data():
	issues, model = generate_model_from_government_gazette_issues()
	model.wv.save_word2vec_format('fek.model')

class LawParser:
	"""
		This class hosts the law parser.The law is provided
		in a file (if it exists) and is parsed in order to be
		split in articles and sentences, ready to be stored in
		the database. This class supports insertions, replacements
		and deletions of articles, paragraphs, phrases and periods.
		It can also provide a serializable object for updating the
		database with its contents.
	"""

	def __init__(self, identifier, filename=None):
		"""The constructor of LawParser is responsible for
		reading and parsing the file as well as detecting
		titles, lemmas and articles which are split into sentences
		by find_corpus()

		:param identifier This is the law identifier (for example ν. 1920/1991)
		:param filename (optional) the text file
		"""
		self.lines = []
		self.identifier = identifier
		if filename:
			self.filename = filename
			tmp_lines = []
			with open(filename, 'r') as infile:
				# remove ugly hyphenthation
				while 1 == 1:
					l = infile.readline()
					if not l:
						break
					l = l.replace('-\n', '')
					l = l.replace('\n', ' ')
					tmp_lines.append(l)


			for line in tmp_lines:
				if line == '':
					continue
				else:
					self.lines.append(line)
		self.thesaurus = {}
		self.lemmas = {}
		self.articles = collections.defaultdict(dict)
		self.titles = {}
		self.corpus = {}
		self.sentences =  collections.defaultdict(dict)
		self.find_corpus()

	def __repr__(self):
		return self.identifier

	def __str__(self):
		return self.identifier

	def find_corpus(self):
		"""Analyzes the corpus to articles, paragraphs and
		then sentences
		"""
		idx = []
		for i, line in enumerate(self.lines):
			if line.startswith('Αρθρο:'):
				idx.append(i)

		for j in range(len(idx) - 1):
			x, y = idx[j], idx[j+1]
			self.lines[x]  = self.lines[x].strip(':').replace(':\t', ' ')
			name = self.lines[x].rstrip().strip('Αρθρο: ')
			self.corpus[name] = self.lines[x : y]

		for article in self.corpus.keys():
			for i, line in enumerate(self.corpus[article]):
				if line.startswith('Κείμενο Αρθρου'):
					self.articles[article] = self.corpus[article][i + 1:]
					paragraphs = collections.defaultdict(list)
					current = '0'
					for t in self.articles[article]:
						x = re.search(r'\d+. ', t)
						if x and x.span() == (0, 3):
							current = x.group().strip('. ')
						paragraphs[current].append(t)

					sentences = {}

					for par in paragraphs.keys():
						val = ''.join(paragraphs[par])[1:]
						paragraphs[par] = val
						sentences[par] = list(filter(lambda x: x.rstrip() != '', val.split('. ')))

					self.articles[article] = paragraphs
					self.sentences[article] = sentences

				elif line.startswith('Λήμματα'):
					self.lemmas[article] = self.corpus[article][i + 1].split(' - ')
				elif line.startswith('Τίτλος Αρθρου'):
					self.titles[article] = self.corpus[article][i + 1]

	def __dict__(self):
		return self.serialize()

	def serialize(self):
		"""Returns the object in database-friendly format
		in a dictionary.
		"""
		return {
			'_id' : self.identifier,
			'thesaurus' : self.thesaurus,
			'lemmas' : self.lemmas,
			'titles' : self.titles,
			'articles' : self.sentences
		}

	def add_article(self, article, content, title=None, lemmas=None):
		"""Add article from content
		:param article the article id
		:param content the content in raw text
		:title (optional) title of article
		:lemmas (optional) lemmas for article
		"""
		# prepare context
		article = str(article)
		paragraphs = collections.defaultdict(list)

		paragraph_ids = [par_id.group().strip('. ') for par_id in re.finditer(r'\d+. ', content)]
		paragraph_corpus = list(filter(lambda x : x.rstrip() != '', re.split(r'\d+. ', content)))
		paragraph_corpus = [p.rstrip().lstrip() for p in paragraph_corpus]


		sentences = {}
		paragraphs = {}
		for key, val in itertools.zip_longest(paragraph_ids, paragraph_corpus):
			if key == None or val == None:
				break
			sentences[key] = val.split('. ')
			paragraphs[key] = val

		self.sentences[article] = sentences
		self.articles[article] = paragraphs

		if title:
			self.titles[article] = title
		if lemmas:
			self.lemmas[article] = lemmas

		return self.serialize()

	def remove_article(self, article):
		"""Removal of article based on its id
		:param artitcle id
		"""

		article = str(article)
		assert(article in list(self.articles.keys()))
		del self.sentences[article]
		del self.articles[article]
		del self.corpus[article]
		del self.lemmas[article]
		del self.titles[article]
		return self.serialize()

	def add_paragraph(self, article, paragraph, content):
		"""Addition of paragraph on article
		:article article id
		:paragraph paragraph id
		:content content in raw text to be split into periods
		"""

		article = str(article)
		paragraph = str(paragraph)

		# prepare content for modification
		content = re.sub(r'\d+. ', '', content)

		# add in its full form or split into periods
		self.articles[article][paragraph] = content
		self.sentences[article][paragraph] = content.split('. ')

		return self.serialize()

	def remove_paragraph(self, article, paragraph, content):
		"""Removal of paragraph"""

		article = str(article)
		paragraph = str(paragraph)
		assert(article in list(self.articles.keys()))
		assert(paragraph in list(self.articles[article].keys()))

		del self.articles[article][paragraph]
		del self.sentences[article][paragraph]

		return self.serialize()

	def replace_phrase(self, old_phrase, new_phrase, article=None, paragraph=None):
		"""Replacement of phrase inside document
		:old_phrase phrase to be replaced
		:new_phrase new phrase
		:article optional detect phrase in certain article
		:paragraph optional detect phrase in certain paragraph
		"""

		search_all = (article == None)

		if article:
			delegate_articles = [str(article)]

			if paragraph:
				delegate_paragraphs = [str(paragraph)]
			else:
				delegate_paragraphs = self.sentences[article].keys()
		else:
			delegate_articles = self.articles.keys()

		for article in delegate_articles:
			if search_all:
				delegate_paragraphs = self.articles[article].keys()

			for paragraph in delegate_paragraphs:
				for i, period in enumerate(self.sentences[article][paragraph]):
					self.sentences[article][paragraph][i] = period.replace(old_phrase, new_phrase)

		return self.serialize()

	def remove_phrase(self, old_phrase, article=None, paragraph=None):
		"""Removal of certain phrase i.e. replacement with empty string"""
		
		return self.replace_phrase(old_phrase, '', article, paragraph)

	def insert_phrase(self, position, old_phrase, new_phrase, article=None, paragraph=None):

		assert(position in ['start', 'end', 'before', 'after'])

		if position in ['start', 'end']:
			assert(article and paragraph)

		search_all = (article == None)

		if article:
			delegate_articles = [str(article)]

			if paragraph:
				delegate_paragraphs = [str(paragraph)]
			else:
				delegate_paragraphs = self.sentences[article].keys()
		else:
			delegate_articles = self.articles.keys()

		for article in delegate_articles:
			if search_all:
				delegate_paragraphs = self.articles[article].keys()

			for paragraph in delegate_paragraphs:
				for i, period in enumerate(self.sentences[article][paragraph]):
					span = re.search(old_phrase, period).span()
					if not span:
						continue
					else:
						x, y = span
					if position == 'before':
						new_period = period[:x]  + new_phrase + ' ' + period[x:]
					elif position == 'after':
						new_period = period[:y] + ' ' + new_phrase +  period[y:]

					self.sentences[article][paragraph][i] = new_period

		return self.serialize()

	def replace_period(self, old_period, new_period, article=None, paragraph=None):
		search_all = (article == None)

		if article:
			delegate_articles = [str(article)]

			if paragraph:
				delegate_paragraphs = [str(paragraph)]
			else:
				delegate_paragraphs = self.sentences[article].keys()
		else:
			delegate_articles = self.articles.keys()

		for article in delegate_articles:
			if search_all:
				delegate_paragraphs = self.articles[article].keys()

			for paragraph in delegate_paragraphs:
				for i, period in enumerate(self.sentences[article][paragraph]):
					if old_period == period:
						self.sentences[article][paragraph][i] = new_period

		return self.serialize()

	def remove_period(self, old_period, article=None, paragraph=None):
		search_all = (article == None)

		if article:
			delegate_articles = [str(article)]

			if paragraph:
				delegate_paragraphs = [str(paragraph)]
			else:
				delegate_paragraphs = self.sentences[article].keys()
		else:
			delegate_articles = self.articles.keys()

		for article in delegate_articles:
			if search_all:
				delegate_paragraphs = self.articles[article].keys()

			for paragraph in delegate_paragraphs:
				for i, period in enumerate(self.sentences[article][paragraph]):
					if old_period == period or old_period == period[:-1]:
						del self.sentences[article][paragraph][i]
						return self.serialize()

		return self.serialize()

	def insert_period(self, position, old_period, new_period, article=None, paragraph=None):

		assert(position in ['start', 'end', 'before', 'after'])

		if position in ['start', 'end']:
			assert(article and paragraph)
			if position == 'start':
				self.articles[article][paragraph].insert(0, new_period)
			else:
				self.append_period(new_period, article, paragraph)

		search_all = (article == None)

		if article:
			delegate_articles = [str(article)]

			if paragraph:
				delegate_paragraphs = [str(paragraph)]
			else:
				delegate_paragraphs = self.sentences[article].keys()
		else:
			delegate_articles = self.articles.keys()

		for article in delegate_articles:
			if search_all:
				delegate_paragraphs = self.articles[article].keys()

			for paragraph in delegate_paragraphs:
				for i, period in enumerate(self.sentences[article][paragraph]):
					if period == old_period or old_period == period[:-1]:
						if position == 'before':
							self.articles[article][paragraph].insert(max(0, i-1), new_period)
						elif position == 'after':
							self.articles[article][paragraph].insert(i + 1, new_period)

		return self.serialize()

	def append_period(context, article, paragraph):
		assert(article and paragraph)
		self.sentences[article][paragraph].append(context)

	def query_from_tree(self, tree):
		assert(tree['law']['_id'] == self.identifier)
		if tree['root']['action'] in ['προστίθεται', 'αντικαθίσταται']:

			try:
				content = tree['what']['content']
				context =  tree['what']['context']
			except KeyError:
				raise Exception('Unable to find content or context in tree')

			if context == 'άρθρο':
				return self.add_article(tree['law']['article']['_id'], content)
			elif context == 'παράγραφος':
				print('Too')
				return self.add_paragraph(
					tree['law']['article']['_id'],
					tree['law']['article']['paragraph']['_id'],
					content)

		elif tree['root']['action'] == 'διαγράφεται':

			try:
				context = tree['what']['context']
			except KeyError:
				raise Exception('Unable to find context in tree')

			if context == 'άρθρο':
				return self.remove_article(tree['law']['article']['_id'])
			elif context == 'παράγραφος':
				print('Too')
				return self.remove_paragraph(
					tree['law']['article']['_id'],
					tree['law']['article']['paragraph']['_id'])



		return self.serialize()
