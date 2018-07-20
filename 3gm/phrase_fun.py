import pytest
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
	splitted = tokenizer.tokenizer.split(joined, delimiter='. ')

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

	splitted = tokenizer.tokenizer.split(joined, delimiter='. ')

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
	tree['what']['content'] = detect_phrase_content(s)

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
	subj_phr_regex = r' η (ακόλουθη φράση:|ακόλουθη λέξη:|φράση|λέξη)[^«]«[^»]*»'
	res = re.search(subj_phr_regex, s)
	if not res:
		return ''
	else:
		return get_phr_content(res.group())

def get_phr_content(q):
	extracts, non_extracts = helpers.get_extracts(q, 0)
	try:
		return extracts[0]
	except:
		return ''

def detect_phr_replacement(s):
	subj_rep_phr = r'(με |από )(τη φράση|τη λέξη|τις λέξεις)[^«]«[^»]*»'
	res = re.search(subj_rep_phr, s)
	if not res:
		return ''
	else:
		return get_phr_content(res.group())

def detect_prhase_locations(s, tree):
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

# Tests
def test_phrase():
	import codifier

	law = codifier.codifier.laws['ν. 4511/2018']
	test =  law.sentences['1']['1']

	test1 = replace_phrase(test, 'επίδοσής της στο αντίδικο μέρος', 'foo')
	tmp = '. '.join(test1)
	assert('επίδοσής της στο αντίδικο μέρος' not in tmp and 'foo' in tmp)

	test2 = remove_phrase(test1, 'foo')
	assert('foo' not in '. '.join(test2))

	test3 = insert_phrase(test1, 'appended')
	assert(test3[-1].endswith('appended'))

	test4 = insert_phrase(test1, 'prepended', position='prepend')
	assert(test4[0].startswith('prepended'))

	test5 = insert_phrase(test1, 'boo', position='before', old_phrase='foo')
	tmp = '. '.join(test5)
	assert('boo foo' in tmp)

	test6 = insert_phrase(test1, 'boo', position='after', old_phrase='foo')
	tmp = '. '.join(test6)
	assert('foo boo' in tmp)

	test7 = law.insert_phrase('boo', position='before', old_phrase='επίδοσής της στο αντίδικο μέρος', article='1', paragraph='1')
	import pprint
	pprint.pprint(test7)

def test_phrase_ops():
	s = 'Στην περίπτωση α΄ της παραγράφου 1 του άρθρου 12 του ν. 4067/2012, διαγράφεται η φράση «και το ισχύον ποσοστό κάλυψης»'
	q = 'Στην παράγραφο 2 του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) μετά τη φράση «Ο Μουφτής ασκεί δικαιοδοσία» προστίθεται η φράση «, υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,»'
	r =  'Στο τέλος της υποπερίπτωσης α΄ της περίπτωσης δ΄ της παραγράφου 3 του άρθρου 9 του ν. 4256/2014 (Α΄ 92) προστίθεται η ακόλουθη φράση: «και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).»'
	t = 'Στην παράγραφο 6 του άρθρου 51 η φράση «κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως» αντικαθίσταται από τη λέξη «στα νέα σχολεία»'

	tr = {'phrase': {'old_phrase': 'κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως', 'new_phrase': 'στα νέα σχολεία'}, 'what': {'content': 'κατά το χρόνο που θα οριστούν τα ανωτέρω σχολεία ως'}, 'root': {'action': 'αντικαθίσταται'}}
	qr = {'phrase': {'location': 'after', 'new_phrase': ', υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,', 'old_phrase': 'Ο Μουφτής ασκεί δικαιοδοσία'}, 'what': {'content': ', υπό τις προϋποθέσεις και τις διαδικασίες που ορίζονται στην παράγραφο 4,'}, 'root': {'action': 'προστίθεται'}}
	rr = {'phrase': {'location': 'append', 'new_phrase': 'και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).', 'old_phrase': ''}, 'what': {'content': 'και τις υποχρεώσεις για την υποβολή πληροφοριών κατάπλου και απόπλου, που απορρέουν από την ενωσιακή νομοθεσία και περιγράφονται στο π.δ. 49/2005 (Α΄ 66), όπως έχει τροποποιηθεί και ισχύει, και στο π.δ. 16/2011 (Α΄ 36).'}, 'root': {'action': 'προστίθεται'}}
	sr = {'phrase': {'old_phrase': 'και το ισχύον ποσοστό κάλυψης'}, 'what': {'content': 'και το ισχύον ποσοστό κάλυψης'}, 'root': {'action': 'διαγράφεται'}}

	assert(detect_phrase_components(t,  {'root' : {'action' : 'αντικαθίσταται'}, 'what' : {},  'phrase' : {}}) == tr)
	assert(detect_phrase_components(q,  {'root' : {'action' : 'προστίθεται'}, 'what' : {},  'phrase' : {}}) == qr)
	assert(detect_phrase_components(r,  {'root' : {'action' : 'προστίθεται'}, 'what' : {},  'phrase' : {}}) == rr)
	assert(detect_phrase_components(s,  {'root' : {'action' : 'διαγράφεται'}, 'what' : {},  'phrase' : {}}) == sr)


if __name__ == '__main__':
	test_phrase_ops()
