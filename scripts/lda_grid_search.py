from __future__ import print_function
from time import time

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
import parser
import collections
import numpy as np
import pprint
import re
no_features = 1000
no_top_words = 5

def display_topics(H, W, feature_names, data_samples, no_top_words, no_top_data_samples):
	graph = {}
	topics = {}
	for topic_idx, topic in enumerate(H):
		print("Topic %d:" % (topic_idx))
		topics[topic_idx] = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]

		print(" ".join(topics[topic_idx]))
		top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_data_samples]
		for doc_index in top_doc_indices:
			print(issues[doc_index].filename)
			graph[doc_index] = list ( filter( lambda x : x != doc_index,  top_doc_indices ))

	print(graph)
	print(topics)
	return graph

def connected_components(graph):
	visited = {}
	components = []
	for u in graph.keys():
		visited[u] = False
	for s in visited.keys():
		if visited[s]:
			continue
		else:
			component = []
			q = collections.deque()
			q.append(s)
			visited[s] = True
			while q:
				p = q.popleft()
				component.append(p)
				for r in graph[p]:
					if not visited[r]:
						q.append(r)
						visited[r] = True
			components.append(component)

	return components

def get_edges(graph):
	E = []
	for u in graph.keys():
		for v in graph[u]:
			E.append([u, v])
	return E


greek_stopwords = []
cnt_swords = 300

with open('../data/el.dat') as f:
	for i in range(cnt_swords):
		line = f.readline()
		if not line:
			break
		line = line.split(' ')
		greek_stopwords.append(line[0])


issues = parser.get_issues_from_dataset()
issues_dict = {}

data_samples = []

for i, issue in enumerate(issues):
	data_samples.append(re.sub("\d+", " ", ''.join( issue.articles.values())))
	issues_dict[i] = issue

n_samples = len(data_samples)
n_components = 10

words = []
for x in data_samples:
	words.extend(x.split(' '))

counter = collections.Counter(words)
gg_most_common = 350
for w in counter.most_common(gg_most_common):
	greek_stopwords.append(w[0])

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words=greek_stopwords)
tfidf = tfidf_vectorizer.fit_transform(data_samples)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words=greek_stopwords)
tf = tf_vectorizer.fit_transform(data_samples)
tf_feature_names = tf_vectorizer.get_feature_names()

no_topics = 10

# Run NMF
nmf_model = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
nmf_W = nmf_model.transform(tfidf)
nmf_H = nmf_model.components_

# Run LDA
lda_model = GridSearchCV(cv=None, error_score='raise',
	estimator=LatentDirichletAllocation(batch_size=128, doc_topic_prior=None,
	evaluate_every=-1, learning_decay=0.7, learning_method=None,
	learning_offset=10.0, max_doc_update_iter=100, max_iter=10,
	mean_change_tol=0.001, n_components=10, n_jobs=1,
	n_topics=None, perp_tol=0.1, random_state=None,
	topic_word_prior=None, total_samples=1000000.0, verbose=0),
	fit_params=None, iid=True, n_jobs=1,
	param_grid={'n_topics': [10, 15, 20, 25, 30], 'learning_decay': [0.5, 0.7, 0.9]},
	pre_dispatch='2*n_jobs', refit=True, return_train_score='warn',
	scoring=None, verbose=0)
lda_model.fit(tf)

lda_W = lda_model.transform(tf)
lda_H = lda_model.components_

no_top_words = 5
no_top_data_samples = 3
graph_nmf = display_topics(nmf_H, nmf_W, tfidf_feature_names, data_samples, no_top_words, no_top_data_samples)
graph_lda = display_topics(lda_H, lda_W, tf_feature_names, data_samples, no_top_words, no_top_data_samples)
print('Breadth first Search for Connected Components for NMF')
cc_nmf = connected_components(graph_nmf)
print(cc_nmf)
print('Filenames')
for c in cc_nmf:
	print([issues[d].filename for d in c])

print('\nBreadth first Search for Connected Components for Latent Dirichlet Allocation')
cc_lda = connected_components(graph_lda)
print(cc_lda)
print('Filenames')
for c in cc_lda:
	print([issues[d].filename for d in c])


print("Log Likelihood: ", lda_model.score(tfidf))

print("Perplexity: ", lda_model.perplexity(tfidf))
