from __future__ import print_function
from time import time

# Matplotlib and scikit
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import NMF, LatentDirichletAllocation

# Helper Functions
from helpers import connected_components, get_edges
import parser
import collections
import numpy as np
import sys
import pprint
import re
import codifier
import database


sys.path.insert(0, '../resources')
import greek_lemmas


db = database.Database()


def process_topics(
		H,
		W,
		feature_names,
		data_samples,
		no_top_words,
		no_top_data_samples):
	graph = {}
	topics = {}
	for topic_idx, topic in enumerate(H):


		print("Topic %d:" % (topic_idx))
		topics[topic_idx] = [feature_names[i]
							 for i in topic.argsort()[:-no_top_words - 1:-1]]

		print(" ".join(topics[topic_idx]))
		top_doc_indices = np.argsort(W[:, topic_idx])[
			::-1][0:no_top_data_samples]


		similar = []
		for doc_index in top_doc_indices:
			print(indices[doc_index])
			similar.append(indices[doc_index])
			graph[doc_index] = list(
				filter(
					lambda x: x != doc_index,
					top_doc_indices))

		s = {
			'_id' : topic_idx,
			'keywords' : topics[topic_idx],
			'statutes' : similar

		}

		global db

		db.topics.save(s)



	print(graph)
	print(topics)
	return graph, topics, top_doc_indices




greek_stopwords = []
cnt_swords = 300

with open('../resources/greek_stoplist.dat') as f:
	for i in range(cnt_swords):
		line = f.readline()
		if not line:
			break
		line = line.split(' ')
		greek_stopwords.append(line[0])



data_samples = []
indices = {}

min_size = 4

i = 0
for law in codifier.codifier.laws.keys():
	print(law)
	corpus = codifier.codifier.get_law(law)
	tmp = corpus.split(' ')
	corpus = []
	for j, word in enumerate(tmp):
		if tmp[j].isdigit() or len(tmp[j]) < min_size:
			continue
		try:
			corpus.append(greek_lemmas.lemmas[word])
		except BaseException:
			corpus.append(word)

	corpus = ' '.join(corpus)

	data_samples.append(corpus)
	indices[i] = law

	i += 1

words = []

for x in data_samples:
	words.extend(x.split(' '))

print('Counting words')
counter = collections.Counter(words)
gg_most_common = 350
for w in counter.most_common(gg_most_common):
	greek_stopwords.append(w[0])

print('Done')


# Initial Parameters
no_features = 1000
no_top_words = 5
n_samples = len(data_samples)

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(
	max_df=0.95,
	min_df=2,
	max_features=no_features,
	stop_words=greek_stopwords)
tfidf = tfidf_vectorizer.fit_transform(data_samples)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic
# graphical model
tf_vectorizer = CountVectorizer(
	max_df=0.95,
	min_df=2,
	max_features=no_features,
	stop_words=greek_stopwords)
tf = tf_vectorizer.fit_transform(data_samples)
tf_feature_names = tf_vectorizer.get_feature_names()

no_topics = 10

# Run NMF
nmf_model = NMF(
	n_components=no_topics,
	random_state=1,
	alpha=.1,
	l1_ratio=.5,
	init='nndsvd').fit(tfidf)
nmf_W = nmf_model.transform(tfidf)
nmf_H = nmf_model.components_

# Run LDA after finding optimal parameters
model = GridSearchCV(
	cv=None,
	error_score='raise',
	estimator=LatentDirichletAllocation(
		batch_size=128,
		doc_topic_prior=None,
		evaluate_every=-1,
		learning_decay=0.7,
		learning_method='batch',
		learning_offset=10.0,
		max_doc_update_iter=100,
		max_iter=10,
		mean_change_tol=0.001,
		n_components=None,
		n_jobs=1,
		perp_tol=0.1,
		random_state=None,
		topic_word_prior=None,
		total_samples=1000000.0,
		verbose=0),
	fit_params=None,
	iid=True,
	n_jobs=1,
	param_grid={
		'n_components': range(
			10,
			31,
			5),
		'learning_decay': [
			0.5,
			0.7,
			0.9]},
	pre_dispatch='2*n_jobs',
	refit=True,
	return_train_score='warn',
	scoring=None,
	verbose=0)
model.fit(tfidf)

# Best Model
lda_model = model.best_estimator_

# Model Parameters
print('LDA Model')
print("Best Model's Params: ", model.best_params_)

# Log Likelihood Score from grid search
print("Best Log Likelihood Score: ", model.best_score_)
print("Best Perplexity Score: ", lda_model.perplexity(tfidf))


lda_W = lda_model.transform(tf)
lda_H = lda_model.components_

no_top_words = 5
no_top_data_samples = 200
graph_nmf, topics, top_doc_indices = process_topics(
	nmf_H,
	nmf_W,
	tfidf_feature_names,
	data_samples,
	no_top_words,
	no_top_data_samples)
graph_lda, topics, top_doc_indices = process_topics(
	lda_H,
	lda_W,
	tf_feature_names,
	data_samples,
	no_top_words,
	no_top_data_samples)

print('Breadth first Search for Connected Components for NMF')
cc_nmf = connected_components(graph_nmf)
print(cc_nmf)
print('Filenames')
for c in cc_nmf:
	print([codifier.codifier.laws[indices[d]] for d in c])

print('\nBreadth first Search for Connected Components for Latent Dirichlet Allocation')
cc_lda = connected_components(graph_lda)
print(cc_lda)
print('Filenames')
for c in cc_lda:
	print([codifier.codifier.laws[indices[d]] for d in c])
