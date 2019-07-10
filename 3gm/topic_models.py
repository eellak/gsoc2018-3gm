from multiprocessing import cpu_count

# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import NMF, LatentDirichletAllocation

# Imports
from helpers import connected_components, get_edges
import parser
import collections
import numpy as np
import sys
import pprint
import re
import codifier
import database
import math
import pickle
import string

# spacy
import spacy

import el_core_news_sm
nlp = el_core_news_sm.load(max_length=2000000)

sys.path.insert(0, '../resources')
import greek_lemmas


db = database.Database()


def contains_digit_or_num(i): return any(
    j.isdigit() or j in string.punctuation for j in i)


def process_topics(
        H,
        W,
        feature_names,
        data_samples,
        no_top_words,
        no_top_data_samples,
        indices):
    graph = {}
    topics = {}
    global db
    db.drop_topics()
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
            '_id': topic_idx,
            'keywords': topics[topic_idx],
            'statutes': similar

        }

        db.topics.save(s)

    print(graph)
    print(topics)
    return graph, topics, top_doc_indices


def build_greek_stoplist(cnt_swords=300):
    greek_stopwords = []

    with open('../resources/greek_stoplist.dat') as f:
        for i in range(cnt_swords):
            line = f.readline()
            if not line:
                break
            line = line.split(' ')
            greek_stopwords.append(line[0])

    return greek_stopwords


def build_data_samples(min_size=4, use_spacy=True):
    data_samples = []
    indices = {}

    i = 0
    for law in codifier.codifier.laws.keys():
        print(law)
        corpus = codifier.codifier.laws[law].export_law('str')
        if use_spacy:
            tmp = nlp(corpus)
        else:
            tmp = corpus.split(' ')
        corpus = []
        for j, word in enumerate(tmp):
            if contains_digit_or_num(word.text) or len(word.text) < min_size:
                continue
            try:
                if use_spacy:
                    try:
                        corpus.append(greek_lemmas[word.lemma_])
                    except BaseException:
                        corpus.append(greek_lemmas[word])
                else:
                    corpus.append(greek_lemmas[word])
            except BaseException:
                corpus.append(str(word))

        corpus = ' '.join(corpus)

        data_samples.append(corpus)
        indices[i] = law

        i += 1

    return data_samples, indices


def build_gg_stoplist(data_samples, greek_stopwords, gg_most_common=500):
    words = []
    for x in data_samples:
        words.extend(x.split(' '))
    print('Counting words')

    try:
        counter = pickle.load(open('gg_stoplist.pickle', 'rb'))
    except BaseException:
        counter = collections.Counter(words)
        pickle.dump(counter, open('gg_stoplist.pickle', 'wb'))
    finally:
        for w in counter.most_common(gg_most_common):
            greek_stopwords.append(w[0])
    print('Done Counting')
    return greek_stopwords, words


def display_components(graph_lda):
    print('\nBreadth first Search for Connected Components for Latent Dirichlet Allocation')
    cc_lda = connected_components(graph_lda)
    print(cc_lda)
    print('Statutes')
    for c in cc_lda:
        print([codifier.codifier.laws[indices[d]] for d in c])


def build_topics(use_spacy=True):
    greek_stopwords = build_greek_stoplist()
    data_samples, indices = build_data_samples(use_spacy=use_spacy)
    greek_stopwords, words = build_gg_stoplist(data_samples, greek_stopwords)

    # Initial Parameters
    no_features = 1000  # Number of features
    n_samples = len(data_samples)  # Len of data samples
    no_top_words = 100  # Number of top words in each topic
    n_components = 100  # Number of topics
    # How many correlations under each topic
    no_top_data_samples = math.ceil(n_samples / n_components)

    # LDA can only use raw term counts for LDA because it is a probabilistic
    # graphical model
    tf_vectorizer = CountVectorizer(
        max_df=0.95,
        min_df=2,
        max_features=no_features,
        stop_words=greek_stopwords)
    tf = tf_vectorizer.fit_transform(data_samples)
    tf_feature_names = tf_vectorizer.get_feature_names()

    lda_model = LatentDirichletAllocation(n_components=n_components,
                                          max_iter=10,
                                          learning_method='online',
                                          learning_offset=50.,
                                          verbose=1,
                                          n_jobs=cpu_count() - 1,
                                          random_state=0)
    lda_model.fit(tf)

    print("Best Perplexity Score: ", lda_model.perplexity(tf))

    lda_W = lda_model.transform(tf)
    lda_H = lda_model.components_

    graph_lda, topics, top_doc_indices = process_topics(
        lda_H,
        lda_W,
        tf_feature_names,
        data_samples,
        no_top_words,
        no_top_data_samples,
        indices)

    pickle.dump(lda_model, open('lda_model.pickle', 'wb'))
    pickle.dump(tf, open('tf.pickle', 'wb'))


if __name__ == '__main__':
    use_spacy = '--spacy' in sys.argv[1:]
    build_topics(use_spacy=use_spacy)
