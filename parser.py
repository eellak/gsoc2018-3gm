#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import date, datetime, time

date_regex = re.compile('(\
([1-9]|0[1-9]|[12][0-9]|3[01])\
[-/.\s+]\
(1[1-2]|0[1-9]|[1-9]|Ιανουαρίου|Φεβρουαρίου|Μαρτίου|Απριλίου|Μαΐου|Ιουνίου|Ιουλίου|Αυγούστου|Νοεμβρίου|Δεκεμβρίου|Σεπτεμβρίου|Οκτωβρίου|Ιαν|Φεβ|Μαρ|Απρ|Μαϊ|Ιουν|Ιουλ|Αυγ|Σεπτ|Οκτ|Νοε|Δεκ)\
(?:[-/.\s+](1[0-9]\d\d|20[0-9][0-8]))?)')


def edit_distance(str1, str2, weight = lambda s1,s2, i, j: 0.75 if s1[i-1] == ' ' or s2[j-1] == ' ' else 1):
		m, n = len(str1), len(str2)
		dp = [[0 for x in range(n+1)] for x in range(m+1)]

		for i in range(m+1):
			for j in range(n+1):

				if i == 0:
					dp[i][j] = j

				elif j == 0:
					dp[i][j] = i
				elif str1[i-1] == str2[j-1]:
					dp[i][j] = dp[i-1][j-1]

				else:
					dp[i][j] = weight(str1,str2,i,j) + min(dp[i][j-1],
									   dp[i-1][j],
									   dp[i-1][j-1])
		return dp[m][n]

MONTHS_PREFIXES = {
	'Ιανουαρίο' : 1,
	'Φεβρουαρίο' : 2,
	'Μαρτίο' : 3,
	'Απριλίο' : 4,
	'Μαΐο' : 5,
	'Ιουνίο' : 6,
	'Ιουλίο' : 7,
	'Αυγούστο' : 8,
	'Σεπτέμβριο' : 9,
	'Οκτωβρίο' : 10,
	'Νοεμβρίο' : 11,
	'Δεκεμβρίο' : 12,
}

class IssueParser:

	def __init__(self, filename, toTxt = False):
		self.filename = filename
		self.lines  = []
		with open(filename, 'r') as infile:
			self.lines = infile.read().splitlines()
		self.dates = []
		self.find_dates()
		self.articles = {}
		self.find_articles()


	def find_dates(self):
		for i, line in enumerate(self.lines):
			result = date_regex.findall(line)
			if result != []:
				self.dates.append((i, result))

		if self.dates == []:
			raise Exception('Could not find dates!')

		full, day, month, year = self.dates[0][1][0]
		print(full)

		for m in MONTHS_PREFIXES.keys():
			if month == m + 'υ':
				month = MONTHS_PREFIXES[m]
				break

		self.issue_date = date(int(year), month, int(day))
		print(self.issue_date)

		return self.dates

	def find_articles(self):
		article_indices = []
		for i, line in enumerate(self.lines):
			if line.startswith('Άρθρο') or line.startswith('Ο Πρόεδρος της Δημοκρατίας'):
				article_indices.append((i, line))
				self.articles[line] = ''


		for j in range(len(article_indices) - 1):
			self.articles[article_indices[j][1]] = ''.join(self.lines[article_indices[j][0] + 1 :  article_indices[j+1][0]])

		# TODO fix hyphenation	
		print(self.articles['Άρθρο 1'])









test = IssueParser('test.txt')
