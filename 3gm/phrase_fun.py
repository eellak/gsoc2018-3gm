import tokenizer
import re
import entities
import helpers

def replace_phrase(
		s,
		old_phrase,
		new_phrase):
	"""Replacement of phrase inside document
	:old_phrase phrase to be replaced
	:new_phrase new phrase
	:article optional detect phrase in certain article
	:paragraph optional detect phrase in certain paragraph
	"""

	joined = '. '.join(s)
	joined = re.sub(old_phrase, new_phrase, joined)
	splitted = tokenizer.tokenizer.split(joined, False, '. ')

	return splitted

def remove_phrase(s, old_phrase):
	return replace_phrase(s, old_phrase, '')

def insert_phrase(
		s,
		new_phrase,
		position='append',
		old_phrase=''):

	"""Phrase insertion with respect to another phrase"""

	joined = '. '.join(s)

	if position == 'prepend':
		joined = new_phrase + ' ' + joined
	elif position == 'append':
		joined = joined + ' ' + new_phrase
	elif position in ['before', 'after']:
		assert(old_phrase != '')
		if position == 'before':
			rep = new_phrase + ' ' + old_phrase
		elif position == 'after':
			rep = old_phrase + ' ' + new_phrase
		else:
			raise Exception('Not a valid position')
		q = replace_phrase(s, old_phrase, rep)
		joined = '. '.join(q)

	splitted = tokenizer.tokenizer.split(joined, False, '. ')

	return splitted

def get_cases(s):
	cases = []
	for i, x in enumerate(s):
		if 1 <= len(x) <= 4:
			try:
				n = entities.Numerals.GreekNum(x)
				cases.append((i, n, n.value))
			except:
				pass
	if cases != []:
		if cases[0][2] != 1:
			n = entities.Numerals.GreekNum('α')
			cases.insert(0, (0, n, n.value))

	return cases

def detect_phrase_components(s, tree):
	'''Detect phrase components given a tree.
	:params s : The region of interest
	:params tree : The syntax tree as argument
	'''
	tree['what']['content'] = detect_phrase_content(s)
	tree['what']['number'] = ['phrase']

	if tree['root']['action'] in ['προστίθεται', 'προστίθενται']:
		tree['phrase']['new_phrase'] = detect_phrase_content(s)
		tree = detect_prhase_locations(s, tree)

	elif tree['root']['action'] in ['διαγράφεται', 'διαγράφονται', 'καταργείται', 'καταργούνται']:
		tree['phrase']['old_phrase'] = detect_phrase_content(s)

	elif tree['root']['action'] in ['αντικαθίσταται', 'αντικαθίστανται']:
		tree['phrase']['old_phrase'] = detect_phrase_content(s)
		tree['phrase']['new_phrase'] = detect_phr_replacement(s)

	return tree

def detect_phrase_content(s):
	"""Detect phrasal content at nsubj position"""
	subj_phr_regex = r' η (ακόλουθη φράση:|ακόλουθη λέξη:|φράση|λέξη)[^«]«[^»]*»'
	res = re.search(subj_phr_regex, s)
	if not res:
		return ''
	else:
		return get_phr_content(res.group())

def get_phr_content(q):
	"""Given a query it returns the portion enclosed in quotes
	:params q : Query string"""
	extracts, non_extracts = helpers.get_extracts(q, 0)
	try:
		return extracts[0]
	except:
		return ''

def detect_phr_replacement(s):
	"""Detect the phrase that will replace another phrase
	:params s : Query string"""
	subj_rep_phr = r'(με |από )(τη φράση|τη λέξη|τις λέξεις)[^«]«[^»]*»'
	res = re.search(subj_rep_phr, s)
	if not res:
		return ''
	else:
		return get_phr_content(res.group())

def detect_prhase_locations(s, tree):
	"""Detect new phrase placement location"""
	subj_before_phr = r'πριν (από |)(τη φράση|τη λέξη|τις λέξεις)[^«]«[^»]*»'
	subj_after_phr = r'μετά (από |)(τη φράση|τη λέξη|τις λέξεις)[^«]«[^»]*»'

	before_res = re.search(subj_before_phr, s)
	if before_res:
		tree['phrase']['location'] = 'before'
		tree['phrase']['old_phrase'] = get_phr_content(before_res.group())

	after_res = re.search(subj_after_phr, s)
	if after_res:
		tree['phrase']['location'] = 'after'
		tree['phrase']['old_phrase'] = get_phr_content(after_res.group())

	if not after_res and not before_res:
		if 'αρχή' in s:
			tree['phrase']['location'] = 'prepend'
		else:
			tree['phrase']['location'] = 'append'
		tree['phrase']['old_phrase'] = ''

	return tree
