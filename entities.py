import re
import numpy as np
from helpers import *

class Minister:

	def __init__(self, name, middle, surname, ministry):
		self.name = name
		self.surname = surname
		self.ministry = ministry
		self.middle = middle

	def is_mentioned(self, s):
		search_full = re.search(self.name + ' ' + self.surname, s)
		if search_full != None:
			return search_full.span()
		search_sur = re.search(self.surname, s)
		if search_sur != None:
			return search_sur.span()
		search_min = re.search(self.ministry, s)
		if search_min != None:
			return search_min.span()

	def __repr__(self):
		return '{} {}'.format(self.name, self.surname)

class Action:

	def __init__(self, name, lemma, derivatives = [], weight_vector = None):
		self.name = name
		self.lemma = lemma
		self.derivatives = derivatives
		self.derivatives.append(name)
		if weight_vector == None:
			self.weight_vector = ( 1 / (len(self.derivatives)) ) * np.ones(len(self.derivatives))
		else:
			self.weight_vector = weight_vector

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

	def score(self, word, _normalize_word = True):
		scores = np.zeros(  len(self.derivatives) )
		for i, derivative in enumerate( self.derivatives ):
			scores[i] = edit_distance(word if not _normalize_word else normalize_word(word), derivative)
		return np.dot(scores, self.weight_vector)




ministers = [
	Minister('ΠΡΟΚΟΠΙΟΣ', 'Β.', 'ΠΑΥΛΟΠΟΥΛΟΣ', 'ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'),
	Minister('ΔΗΜΟΣ', '', 'ΠΑΠΑΔΗΜΗΤΡΙΟΥ', 'Οικονομίας και Ανάπτυξης'),
	Minister('ΕΛΕΝΑ', '', 'ΚΟΥΝΤΥΡΑ', 'Τουρισμού'),
	Minister('ΣΤΑΥΡΟΣ', '', 'ΚΟΝΤΟΝΗΣ', 'Δικαιοσύνης'),
	Minister('ΚΩΝΣΤΑΝΤΙΝΟΣ', '', 'ΓΑΒΡΟΓΛΟΥ', 'Παιδείας, Έρευνας και Θρησκευμάτων')
]

actions = [
	Action('προστίθεται', 'add', ['προσθέτουμε', 'προσθήκη']),
	Action('διαγράφεται', 'delete', ['διαγράφουμε', 'διαγραφή']),
	Action('παύεται', 'terminate', ['παύση', 'παύουμε']),
	Action('τροποποιείται', 'amend', ['τροποποίηση', 'τροποποιούμε']),
	Action('αντικαθίσταται','replace', ['αντικαθίσταται', 'αντικατάσταση'])
]

# Simple Classifier that uses Levenstein Distance
class EditDistanceClassifier:

	@staticmethod
	def classify_word(word, threshold = 5):
		global actions
		result = np.zeros(len(actions))
		for i, action in enumerate ( actions ) :
			result[i] = action.score(word)
		amin = np.argmin(result)
		if result[amin] < threshold:
			return actions[amin], result[amin]
		else:
			return None, -1

	@staticmethod
	def classify_extract(extract):
		l = extract.split(' ')
		d = list ( filter(lambda x : x[0] != None, [EditDistanceClassifier.classify_word(w) for w in l]) )
		print(d)
		amin = 0
		for i in range (len (d)):
			if d[i][1] < d[amin][1]: amin = i

		print('Smallest hamming = {}, dist = {}'.format(d[amin], l[amin]))
